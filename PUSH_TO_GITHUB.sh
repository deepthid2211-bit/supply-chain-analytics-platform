#!/bin/bash
# Push Supply Chain Analytics Platform to GitHub
# Run this script after creating your GitHub repository

echo "🚀 Pushing Supply Chain Analytics Platform to GitHub..."
echo ""

# Check if git is configured
if ! git config user.email > /dev/null; then
    echo "Configuring git..."
    git config --global user.email "deepthid2211@gmail.com"
    git config --global user.name "Deepthi Desharaju"
fi

echo "✅ Git configured"
echo ""

# Prompt for GitHub username
read -p "Enter your GitHub username: " GITHUB_USERNAME

echo ""
echo "📝 Next steps:"
echo "1. Go to: https://github.com/new"
echo "2. Repository name: supply-chain-analytics-platform"
echo "3. Description: End-to-end supply chain analytics with Snowflake, dbt, and ML"
echo "4. Make it PUBLIC"
echo "5. DO NOT initialize with README"
echo "6. Click 'Create repository'"
echo ""
read -p "Press Enter when repository is created..."

echo ""
echo "🔗 Adding GitHub remote..."
git remote remove origin 2>/dev/null  # Remove if exists
git remote add origin "https://github.com/$GITHUB_USERNAME/supply-chain-analytics-platform.git"

echo "✅ Remote added"
echo ""

echo "📤 Pushing to GitHub..."
git branch -M main
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ ✅ ✅ SUCCESS! ✅ ✅ ✅"
    echo ""
    echo "🎉 Your project is now live on GitHub!"
    echo ""
    echo "🔗 View it at:"
    echo "   https://github.com/$GITHUB_USERNAME/supply-chain-analytics-platform"
    echo ""
    echo "📋 Next steps:"
    echo "1. Go to your GitHub repo"
    echo "2. Add topics (tags): snowflake, dbt, python, machine-learning, analytics"
    echo "3. Star your own repo!"
    echo "4. Share the link on LinkedIn!"
    echo ""
else
    echo ""
    echo "❌ Push failed. Common issues:"
    echo "1. Need to authenticate - use personal access token"
    echo "2. Repository name doesn't match"
    echo "3. Need to verify email on GitHub"
    echo ""
    echo "Let me know the error and I'll help fix it!"
fi
