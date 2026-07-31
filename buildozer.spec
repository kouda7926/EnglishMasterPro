name: Build Android APK

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install system dependencies
        run: |
          sudo apt-get update
          sudo apt-get install -y \
            openjdk-17-jdk \
            autoconf \
            libtool \
            pkg-config \
            zlib1g-dev \
            libncurses5-dev \
            libncursesw5-dev \
            cmake \
            libffi-dev \
            libssl-dev \
            automake \
            build-essential \
            clang \
            lld

      - name: Install Python dependencies
        run: |
          pip install --upgrade pip setuptools wheel
          pip install buildozer kivy

      - name: Build APK
        env:
          BUILDOZER_WARN_ON_ROOT: 0
        run: |
          buildozer -y android debug

      - name: Upload APK
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: EnglishMasterPro-APK
          path: bin/*.apk
          retention-days: 14
          if-no-files-found: ignore
