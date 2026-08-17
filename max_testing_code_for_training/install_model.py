from huggingface_hub import snapshot_download

MODEL_NAME = "Qwen/Qwen3.5-9B"

snapshot_download(
    repo_id=MODEL_NAME,
)

print("Done.")