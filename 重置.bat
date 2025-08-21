rmdir /s /q .git
git init
git branch -m main
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/ayyayyayy2002/BilibiliVideoAutoReport.git
git push -f origin main
pause