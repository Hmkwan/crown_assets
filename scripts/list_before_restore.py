import glob,os
files=glob.glob('app.db.before_restore_*')
files.sort()
for f in files:
    st=os.stat(f)
    print(f, st.st_size, st.st_mtime)
