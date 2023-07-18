import aiohttp, asyncio, bs4, fake_useragent, re, json, builtins, tempfile, sys, huggingface_hub, zhconv, argparse, os
parser = argparse.ArgumentParser()
parser.add_argument('huggingface')

huggingface_hub.login(parser.parse_args().huggingface) #https://huggingface.co/settings/tokens
unlink = []

async def main():
    async with aiohttp.ClientSession(headers={'user-agent':fake_useragent.UserAgent().chrome}) as client:
        async with client.get('https://www.iole.tv/vodplay/29429-1-2.html') as episode:
            html = bs4.BeautifulSoup(await episode.text(), 'lxml')
            async with client.get(json.loads(html.find('script', string=re.compile('m3u8')).string.replace('var player_aaaa=', '')).get('url')) as m3u8:
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    sys.modules[__name__].unlink += tmp.name,
                    ffmpeg = await asyncio.create_subprocess_exec('ffmpeg', '-y', '-protocol_whitelist', 'http,https,file,tls,tcp,pipe,crypto', '-i', '-', '-f', 'mp4', tmp.name, stdin=asyncio.subprocess.PIPE)
                    await ffmpeg.communicate(await m3u8.content.read())
                    api = huggingface_hub.HfApi()
                    future = api.upload_file(path_or_fileobj=tmp.name, path_in_repo=''.join((zhconv.convert(html.find('title').string.split()[0], 'zh-cn'), '/', '02', '.mp4')), repo_id='chaowenguo/video', repo_type='model', run_as_future=True)
    return future
  
asyncio.run(main()).result()
for _ in unlink: os.unlink(_)
