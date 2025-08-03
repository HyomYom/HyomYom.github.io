#!/bin/zsh

changed=$(git status --porcelain _posts/*.md)

if [[ -n "$changed" ]]; then
  git add _posts/*.md
  git commit -m "chore: update post(s) on change"
  echo "✅ 자동 커밋 완료"
else
  echo "ℹ️ 변경된 내용 없음"
fi
