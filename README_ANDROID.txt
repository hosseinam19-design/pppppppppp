Davam Samen Card - Android APK

This version fixes the previous GitHub Actions build failure.

ROOT CAUSE OF THE PREVIOUS FAILURE
-----------------------------------
The previous build compiled Python 3.14 while using --ndk-api=23. The Python
3.14 source referenced preadv()/pwritev(), which are not available through the
Android API 23 headers. Compilation therefore failed in Python/remote_debugging.c.

FIXES IN THIS VERSION
---------------------
1. GitHub Actions uses Python 3.12.13.
2. python-for-android is explicitly pinned to the stable master branch.
3. The Android requirement explicitly requests python3==3.12.13.
4. Android NDK is explicitly set to 28c.
5. Android API is 35 and minimum API remains 23.
6. Pillow and the other Python packages are pinned to reproducible versions.
7. Every GitHub build starts with a clean .buildozer/bin directory.
8. The APK is uploaded as the artifact: dovam-samen-card-apk.

HOW TO BUILD
------------
1. Upload/push the complete project to GitHub.
2. Open Actions.
3. Select "Build Android APK".
4. Click "Run workflow" or push to main.
5. After success, open the run and download "dovam-samen-card-apk".
