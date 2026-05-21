import asyncio
from crawl4ai import AsyncWebCrawler
import os
import requests
from bs4 import BeautifulSoup

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

async def extract_video_links(url, crawler, max_retries=3):
    """从给定的URL中提取所有视频链接，带重试机制"""
    for attempt in range(max_retries):
        try:
            result = await crawler.arun(url=url, page_timeout=60000)  # 设置超时时间为 60 秒
            if result and result.html:
                soup = BeautifulSoup(result.html, 'html.parser')
                video_links = []
                for a_tag in soup.find_all('a', class_='overlay', href=True):
                    video_links.append(a_tag['href'])
                return video_links
            else:
                print(f"无法获取 {url} 的HTML内容")
                return []
        except Exception as e:
            print(f"爬取 {url} 过程中发生错误: {e}, 尝试次数: {attempt + 1}/{max_retries}")
            if attempt < max_retries - 1:
                await asyncio.sleep(5)  # 等待 5 秒后重试
            else:
                print(f"达到最大重试次数，放弃爬取 {url}")
                return []
    return []

async def download_videos_from_page(url, crawler, semaphore):
    """从视频页面下载视频"""
    async with semaphore:
        try:
            result = await crawler.arun(
                url=url,
                js_code="""
                let videoLinks = [];
                let videoSources = document.querySelectorAll('video > source');

                videoSources.forEach(source => {
                    videoLinks.push(source.src);
                });

                return videoLinks;
                """
            )
            if result and result.extracted_content:
                video_links = result.extracted_content
                print(f"提取到的视频链接: {video_links}")

                output_dir = r"D:\OneDrive\桌面\video"
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                for i, video_link in enumerate(video_links):
                    filename = os.path.join(output_dir, f"video_{i}.mp4")
                    await download_video(video_link, filename)
            else:
                print(f"无法从 {url} 提取视频链接")
        except Exception as e:
            print(f"下载 {url} 视频过程中发生错误: {e}")

async def main():
    """主函数，用于设置起始URL并开始爬取和下载视频"""
    start_url = "https://hanime1.me/watch?v=105501"

    # 限制并发任务的数量
    semaphore = asyncio.Semaphore(5)  # 允许最多 5 个并发任务

    async with AsyncWebCrawler(verbose=True) as crawler:
        video_links = await extract_video_links(start_url, crawler)

        if video_links:
            print(f"找到以下视频链接: {video_links}")
            tasks = [download_videos_from_page(link, crawler, semaphore) for link in video_links]
            await asyncio.gather(*tasks)
        else:
            print("未找到任何视频链接")

if __name__ == "__main__":
    asyncio.run(main())