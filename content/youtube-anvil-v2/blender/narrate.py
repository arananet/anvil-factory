"""Per section narration with edge-tts. Text is parsed from script.md exactly as written."""
import asyncio, re, sys, pathlib
import edge_tts
root = pathlib.Path(__file__).resolve().parent.parent
rate = sys.argv[1] if len(sys.argv) > 1 else "+0%"
txt = (root / "script.md").read_text()
nar = txt.split("## Narration")[1].split("## Notes")[0]
blocks = re.split(r"^### \d+\..*$", nar, flags=re.M)[1:]
async def main():
    for i, b in enumerate(blocks, 1):
        body = "\n".join(l for l in b.strip().splitlines() if not l.startswith("Target timing")).strip()
        await edge_tts.Communicate(body, "en-US-ChristopherNeural", rate=rate).save(str(root / "audio" / f"s{i}.mp3"))
        print(i, len(body.split()), "words")
asyncio.run(main())
