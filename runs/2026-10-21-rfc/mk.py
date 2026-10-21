import json
fm=json.load(open('fm.json'))
open('post.md','w').write("---\n"+json.dumps(fm,indent=1,ensure_ascii=False)+"\n---\n"+open('body.md').read())
