import aiohttp, asyncio, bs4, fake_useragent, re, pyjsparser, builtins, tempfile, sys, huggingface_hub, zhconv, argparse, os
parser = argparse.ArgumentParser()
parser.add_argument('huggingface')

huggingface_hub.login(parser.parse_args().huggingface) #https://huggingface.co/settings/tokens
unlink = []

async def main():
    async with aiohttp.ClientSession(headers={'user-agent':fake_useragent.UserAgent().chrome}) as client:
        async with client.get('https://www.iole.tv/vodplay/29429-1-1.html') as episode:
            html = bs4.BeautifulSoup(await episode.text(), 'lxml')
            async with client.get(builtins.next(m3u8.get('value') for _ in pyjsparser.parse(html.find('script', string=re.compile('m3u8')).string).get('body')[0].get('declarations')[0].get('init').get('properties') if _.get('value').get('type') == 'Literal' and 'm3u8' in (m3u8 := _.get('value')).get('raw'))) as m3u8:
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    sys.modules[__name__].unlink += tmp.name,
                    ffmpeg = await asyncio.create_subprocess_exec('ffmpeg', '-y', '-protocol_whitelist', 'http,https,file,tls,tcp,pipe', '-i', '-', '-f', 'mp4', tmp.name, stdin=asyncio.subprocess.PIPE)
                    await ffmpeg.communicate(await m3u8.content.read())
                    api = huggingface_hub.HfApi()
                    future = api.upload_file(path_or_fileobj=tmp.name, path_in_repo=''.join((zhconv.convert(html.find('title').string.split()[0], 'zh-cn'), '/', '01', '.mp4')), repo_id='chaowenguo/video', repo_type='model', run_as_future=True)
    return future
  
asyncio.run(main()).result()
for _ in unlink: os.unlink(_)
