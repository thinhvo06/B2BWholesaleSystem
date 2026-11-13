@echo off
set /p REPO_URL="Nhap link GitHub repository cua ban (vi du: https://github.com/username/B2BWholesaleSystem.git): "
if "%REPO_URL%"=="" (
    echo Vui long nhap URL hop le!
    pause
    exit /b
)

echo Dang lien ket remote origin...
git remote remove origin 2>nul
git remote add origin %REPO_URL%

echo Dang day nhanh main len GitHub...
git push -u origin main

echo Dang day nhanh develop len GitHub...
git push -u origin develop

echo Dang day nhanh feature/member1-web-core len GitHub...
git push -u origin feature/member1-web-core

echo.
echo ========================================================
echo DA HOAN TAT DAY CODE VA LICHSU BRANCH LEN GITHUB!
echo ========================================================
pause
