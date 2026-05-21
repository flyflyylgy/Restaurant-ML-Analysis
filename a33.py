import asyncio
import requests
import os

async def download_video(url, filename):
    """下载视频文件"""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # 检查请求是否成功

        with open(filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"视频 {filename} 下载完成")
    except requests.exceptions.RequestException as e:
        print(f"下载 {url} 失败: {e}")

async def main():
    """主函数，用于设置视频链接和文件名，并调用下载函数"""
    video_url = "https://vdownload.hembed.com/105501-1080p.mp4?secure=pKQqnyAcgrxDLxWcSPLiRw==,1745200813"  # 替换为你的视频链接
    output_dir = r"D:\OneDrive\桌面\video"  # 保存视频的目录
    filename = os.path.join(output_dir, "video.mp4")  # 视频保存的完整路径

    # 创建保存视频的目录
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    await download_video(video_url, filename)  # 调用下载函数

if __name__ == "__main__":
    asyncio.run(main())