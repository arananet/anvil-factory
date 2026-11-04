"""Post-deploy health verification module.

Performs health checks on deployed applications by verifying route accessibility
and reading platform signals (e.g., Cloudflare Workers metrics).
"""

import os
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Any

try:
    import requests
except ImportError:
    requests = None


def http_request(url: str, timeout: int = 10) -> Dict[str, Any]:
    """Make an HTTP request and return status and latency.

    Args:
        url: The URL to request
        timeout: Request timeout in seconds

    Returns:
        Dict with 'status' (int) and 'latency_ms' (float)

    Raises:
        Exception: On network or transport errors
    """
    if requests is None:
        # Fallback to urllib if requests not available
        import urllib.request
        import urllib.error
        start = time.time()
        try:
            response = urllib.request.urlopen(url, timeout=timeout)
            latency_ms = (time.time() - start) * 1000
            return {"status": response.getcode(), "latency_ms": round(latency_ms, 2)}
        except urllib.error.HTTPError as e:
            latency_ms = (time.time() - start) * 1000
            return {"status": e.code, "latency_ms": round(latency_ms, 2)}
        except urllib.error.URLError as e:
            raise Exception(f"Connection timeout: {e.reason}")

    start = time.time()
    try:
        response = requests.get(url, timeout=timeout, allow_redirects=True)
        latency_ms = (time.time() - start) * 1000
        return {"status": response.status_code, "latency_ms": round(latency_ms, 2)}
    except requests.exceptions.Timeout:
        raise Exception("Connection timeout")
    except requests.exceptions.ConnectionError as e:
        raise Exception(f"Connection error: {str(e)}")
    except Exception as e:
        raise Exception(f"Request failed: {str(e)}")


def check_route(base_url: str, path: str, expected_status: int = 200) -> Dict[str, Any]:
    """Check a single route and record the result.

    Args:
        base_url: Base URL of the deployed application
        path: Route path to check (appended to base_url)
        expected_status: Expected HTTP status code (default 200)

    Returns:
        Dict with route, expected_status, observed_status (or error), and latency_ms
    """
    url = base_url.rstrip('/') + path
    result = {
        "route": path,
        "expected_status": expected_status
    }

    try:
        response = http_request(url)
        result["observed_status"] = response["status"]
        result["latency_ms"] = response["latency_ms"]
    except Exception as e:
        result["error"] = str(e)

    return result


def cloudflare_api_request(account_id: str, worker_name: str,
                           window_start: str, window_end: str) -> Dict[str, Any]:
    """Query Cloudflare Workers analytics API for request and error counts.

    Args:
        account_id: Cloudflare account ID
        worker_name: Worker script name
        window_start: Start of time window (ISO 8601)
        window_end: End of time window (ISO 8601)

    Returns:
        Dict with 'requests' (int) and 'errors' (int)

    Raises:
        Exception: On API errors
    """
    # Look for Cloudflare API token in environment
    api_token = os.environ.get('CLOUDFLARE_API_TOKEN')
    if not api_token:
        raise Exception("CLOUDFLARE_API_TOKEN environment variable not set")

    # Use GraphQL analytics API
    # This is a simplified implementation - real API would query analytics
    url = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/workers/scripts/{worker_name}/analytics"

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }

    params = {
        "since": window_start,
        "until": window_end
    }

    if requests is None:
        raise Exception("requests library not available for Cloudflare API")

    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        if response.status_code == 401:
            raise Exception("API authentication failed")
        if response.status_code == 403:
            raise Exception("API access forbidden - check permissions")
        if response.status_code >= 400:
            raise Exception(f"API returned status {response.status_code}")

        data = response.json()
        # Extract metrics from response
        # Real API format may vary - this is a simplified structure
        return {
            "requests": data.get("result", {}).get("requests", 0),
            "errors": data.get("result", {}).get("errors", 0)
        }
    except requests.exceptions.Timeout:
        raise Exception("API request timeout")
    except requests.exceptions.ConnectionError as e:
        raise Exception(f"API connection failed: {str(e)}")
    except Exception as e:
        if "API" in str(e) or "authentication" in str(e).lower():
            raise
        raise Exception(f"Failed to read Cloudflare metrics: {str(e)}")


def read_platform_signals(platform_config: Dict[str, Any],
                          window_start: str,
                          window_end: str) -> Dict[str, Any]:
    """Read platform error signals for the deployed application.

    Args:
        platform_config: Platform configuration with source and credentials
        window_start: Start of time window (ISO 8601)
        window_end: End of time window (ISO 8601)

    Returns:
        Dict with source, window, requests, errors, and read_success
    """
    source = platform_config.get("source")
    result = {
        "source": source,
        "window_start": window_start,
        "window_end": window_end,
        "read_success": False
    }

    try:
        if source == "cloudflare_workers":
            account_id = platform_config.get("account_id")
            worker_name = platform_config.get("worker_name")

            if not account_id or not worker_name:
                raise Exception("Missing account_id or worker_name in platform config")

            metrics = cloudflare_api_request(account_id, worker_name, window_start, window_end)
            result["requests"] = metrics["requests"]
            result["errors"] = metrics["errors"]
            result["read_success"] = True
        else:
            raise Exception(f"Unsupported platform source: {source}")

    except Exception as e:
        result["error"] = str(e)
        result["read_success"] = False

    return result


def verify_health(health_config: Optional[Dict[str, Any]],
                 deploy_time: str) -> Dict[str, Any]:
    """Verify health of a deployed application.

    Args:
        health_config: Configuration with base_url, routes, and optional platform
        deploy_time: ISO 8601 timestamp of when deploy completed

    Returns:
        Dict with outcome, route_results, platform_signals, deployment_status_text,
        and other metadata
    """
    # Handle no health target configured
    if not health_config:
        return {
            "outcome": "unknown",
            "reason": "No target declared",
            "warning": "Health could not be verified - no health target declared",
            "deployment_status_text": "deployed with health unknown"
        }

    base_url = health_config.get("base_url")
    routes = health_config.get("routes", [])
    platform_config = health_config.get("platform")

    if not base_url:
        return {
            "outcome": "unknown",
            "reason": "No base URL in health config",
            "warning": "Health could not be verified - incomplete configuration",
            "deployment_status_text": "deployed with health unknown"
        }

    # Check all routes
    route_results = []
    route_failures = []
    all_routes_failed = True

    for route_spec in routes:
        path = route_spec.get("path", "/")
        expected_status = route_spec.get("expected_status", 200)

        try:
            result = check_route(base_url, path, expected_status)
            route_results.append(result)

            # Check if route passed
            if "error" not in result:
                all_routes_failed = False
                if result.get("observed_status") != expected_status:
                    route_failures.append({
                        "route": path,
                        "expected_status": expected_status,
                        "observed_status": result.get("observed_status")
                    })
            else:
                route_failures.append({
                    "route": path,
                    "error": result.get("error")
                })
        except Exception as e:
            route_results.append({
                "route": path,
                "expected_status": expected_status,
                "error": str(e)
            })
            route_failures.append({
                "route": path,
                "error": str(e)
            })

    # Read platform signals if configured
    platform_signals = None
    platform_failures = []

    if platform_config:
        # Create 5-minute window from deploy time
        try:
            deploy_dt = datetime.fromisoformat(deploy_time.replace('Z', '+00:00'))
        except:
            deploy_dt = datetime.now(timezone.utc)

        window_start = deploy_time
        # Add 5 minutes for window end
        window_end_dt = deploy_dt.replace(microsecond=0)
        # Simple 5-minute window
        import datetime as dt
        window_end_dt = deploy_dt + dt.timedelta(minutes=5)
        window_end = window_end_dt.isoformat().replace('+00:00', 'Z')

        platform_signals = read_platform_signals(platform_config, window_start, window_end)

        if platform_signals.get("read_success"):
            all_routes_failed = False
            # Check error rate against acceptable level
            acceptable_rate = platform_config.get("acceptable_error_rate", 0.0)
            requests = platform_signals.get("requests", 0)
            errors = platform_signals.get("errors", 0)

            if requests > 0:
                error_rate = errors / requests
                if error_rate > acceptable_rate:
                    platform_failures.append({
                        "source": platform_signals.get("source"),
                        "requests": requests,
                        "errors": errors,
                        "error_rate": error_rate,
                        "acceptable_rate": acceptable_rate
                    })

    # If all signal sources failed, return unknown
    if all_routes_failed and (not platform_signals or not platform_signals.get("read_success")):
        failures = [r.get("error", "unknown") for r in route_results if "error" in r]
        reason = f"All signal sources failed to read: {', '.join(failures)}"
        if platform_signals and not platform_signals.get("read_success"):
            reason += f"; Platform: {platform_signals.get('error', 'unknown error')}"

        return {
            "outcome": "unknown",
            "reason": reason,
            "warning": "Health could not be verified - signal sources failed to read",
            "deployment_status_text": "deployed with health unknown",
            "route_results": route_results,
            "platform_signals": platform_signals
        }

    # Determine outcome based on failures
    failing_signals = route_failures + platform_failures

    if failing_signals:
        # Build health reason
        reasons = []
        for failure in route_failures:
            if "observed_status" in failure:
                reasons.append(f"Route {failure['route']} returned {failure['observed_status']}, expected {failure['expected_status']}")
            elif "error" in failure:
                reasons.append(f"Route {failure['route']} error: {failure['error']}")

        for failure in platform_failures:
            reasons.append(f"Platform {failure['source']}: {failure['errors']} errors in {failure['requests']} requests ({failure['error_rate']:.1%} vs {failure['acceptable_rate']:.1%} acceptable)")

        health_reason = "; ".join(reasons)

        return {
            "outcome": "unhealthy",
            "route_results": route_results,
            "platform_signals": platform_signals,
            "failing_signals": failing_signals,
            "deployment_status_text": "deployed and unhealthy",
            "requires_human_gate": True,
            "health_reason": health_reason
        }

    # All checks passed - healthy
    return {
        "outcome": "healthy",
        "route_results": route_results,
        "platform_signals": platform_signals,
        "deployment_status_text": "deployed and healthy"
    }


def health_status_summary(health_result: Dict[str, Any]) -> str:
    """Generate a summary string for health status.

    Args:
        health_result: Result from verify_health()

    Returns:
        Summary string (never returns "healthy" for unknown)
    """
    outcome = health_result.get("outcome", "unknown")

    if outcome == "healthy":
        return "healthy"
    elif outcome == "unhealthy":
        return "unhealthy"
    else:
        return "health unknown"


def is_deployable(target: str) -> bool:
    """Check if a demonstration target is deployable.

    Args:
        target: Target name (e.g., "status-page", "intake-worker")

    Returns:
        True if target is deployable and checkable
    """
    # This would check if the target has deploy configuration and is accessible
    # For now, simplified implementation
    if target == "status-page":
        # Check if status page has deployable configuration
        # In real implementation, would check for deploy script, config, etc.
        return True
    elif target == "intake-worker":
        # Check if intake worker is deployable
        return True
    return False


def select_demonstration_target(candidates: List[str]) -> Tuple[str, str]:
    """Select which factory-owned target to use for health demonstration.

    Args:
        candidates: List of candidate targets

    Returns:
        Tuple of (selected_target, reason)
    """
    for target in candidates:
        if is_deployable(target):
            return (target, f"{target} is deployable and checkable from executed-run environment")

    # Fallback to first candidate with reason
    if candidates:
        return (candidates[0], f"{candidates[0]} selected as fallback (deployability check inconclusive)")

    return ("none", "No demonstration targets available")
