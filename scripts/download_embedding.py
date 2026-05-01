"""
下载轻量级词嵌入模型到本地，适配低配置服务器 (2核2G)。
默认下载: BAAI/bge-small-zh-v1.5 (维度 512, 约 100MB)
"""
import argparse
from pathlib import Path

from sentence_transformers import SentenceTransformer


def download_model(model_name: str, save_dir: Path):
    print(f"正在下载模型: {model_name}")
    print(f"保存目录: {save_dir}")
    model = SentenceTransformer(model_name, device="cpu")
    save_dir.mkdir(parents=True, exist_ok=True)
    model.save(str(save_dir))
    print(f"下载完成，已保存到: {save_dir}")

    # 验证
    test_vec = model.encode("测试")
    print(f"向量维度: {len(test_vec)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="下载 Embedding 模型")
    parser.add_argument(
        "--model",
        default="BAAI/bge-small-zh-v1.5",
        help="模型名称 (默认: BAAI/bge-small-zh-v1.5)",
    )
    parser.add_argument(
        "--output",
        default="docker/embedding",
        help="输出目录 (默认: docker/embedding)",
    )
    args = parser.parse_args()

    output_path = Path(args.output) / args.model.replace("/", "_")
    download_model(args.model, output_path)
