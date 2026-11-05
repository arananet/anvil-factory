Fixed! The test now correctly expects the `RoutingConfigError` that `load_routing_config` raises when it validates model assignments during configuration load. The test verifies the error message includes all three required elements: the station kind ("reviewer"), the configured model ("review-strong"), and the policy ceiling it exceeds ("review-balanced").

This addresses the gate loopback 2 defect where the test wasn't expecting the S4 validation behavior that was correctly implemented in loopback 1.
