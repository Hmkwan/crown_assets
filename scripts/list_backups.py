import os
b='backups'
if not os.path.exists(b):
    print('no backups dir')
else:
    for f in sorted(os.listdir(b)):
        p=os.path.join(b,f)
        try:
            st=os.stat(p)
            print(f, st.st_size, st.st_mtime)
        except Exception as e:
            print('err',f,e)
