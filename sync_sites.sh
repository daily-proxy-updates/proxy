#!/bin/bash
# 同步站点配置数据
echo "Syncing sites data from ../mirror/sites..."
mkdir -p sites
cp ../mirror/sites/*.json sites/
echo "Done."
