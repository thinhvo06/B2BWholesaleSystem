param(
    [Parameter(Mandatory=$true)]
    [string]$RepoUrl
)

Write-Host ">>> Đang cấu hình Remote Origin tới: $RepoUrl <<<" -ForegroundColor Cyan

# Remove origin if already exists
git remote remove origin 2>$null

# Add new origin
git remote add origin $RepoUrl

Write-Host ">>> Đang đẩy nhánh 'main' lên GitHub... <<<" -ForegroundColor Yellow
git push -u origin main

Write-Host ">>> Đang đẩy nhánh 'develop' lên GitHub... <<<" -ForegroundColor Yellow
git push -u origin develop

Write-Host ">>> Đang đẩy nhánh tính năng 'feature/member1-web-core' lên GitHub... <<<" -ForegroundColor Yellow
git push -u origin feature/member1-web-core

Write-Host ">>> HOÀN TẤT ĐẨY TOÀN BỘ CẤU TRÚC NHÁNH LÊN GITHUB! <<<" -ForegroundColor Green
Write-Host "Bạn hãy copy link repo này để đưa vào file Readme.txt khi nộp bài." -ForegroundColor Green
