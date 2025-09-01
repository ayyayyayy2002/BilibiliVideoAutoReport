rmdir /s /q .git
git init
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890

git branch -m main
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/ayyayyayy2002/BilibiliVideoAutoReport.git
git push -f origin main
pause