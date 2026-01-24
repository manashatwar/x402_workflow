# x402 Settlement Web Interface

A simple web app to trigger x402 settlement workflows via GitHub Pages.

## 🌐 Live Demo

Once deployed: `https://YOUR_USERNAME.github.io/x402_workflow/`

## 🚀 Deployment to GitHub Pages

### Method 1: Using GitHub Settings (Easiest)

1. **Push the `docs` folder to your repository:**
   ```bash
   git add docs/
   git commit -m "Add GitHub Pages web interface"
   git push origin main
   ```

2. **Enable GitHub Pages:**
   - Go to your repository on GitHub
   - Settings → Pages
   - Source: Deploy from a branch
   - Branch: `main` → `/docs` folder
   - Save

3. **Access your site:**
   - Wait 1-2 minutes for deployment
   - Visit: `https://YOUR_USERNAME.github.io/x402_workflow/`

### Method 2: Using GitHub Actions (Alternative)

Add `.github/workflows/pages.yml`:

```yaml
name: Deploy to GitHub Pages

on:
  push:
    branches: [ main ]
    paths:
      - 'docs/**'
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Pages
        uses: actions/configure-pages@v4
      
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: './docs'
      
      - name: Deploy to GitHub Pages
        uses: actions/deploy-pages@v4
```

## 📋 Features

- ✅ Beautiful, responsive UI
- ✅ All workflow inputs available
- ✅ Form validation
- ✅ localStorage for saving preferences
- ✅ Direct GitHub API integration
- ✅ Real-time status updates
- ✅ Helpful error messages
- ✅ No backend required

## 🔐 Security

- Token stored in browser localStorage only
- Never sent to any external server
- Direct communication with GitHub API
- All data processed client-side

## 🎯 Usage

1. Visit the deployed page
2. Generate a GitHub Personal Access Token:
   - Go to: https://github.com/settings/tokens
   - Generate new token (classic)
   - Select scopes: `repo`, `workflow`
3. Fill in the form
4. Click "Trigger Settlement"
5. Monitor in GitHub Actions tab

## 🛠️ Customization

### Change Default Values

Edit `docs/index.html`:

```javascript
value="YOUR_DEFAULT_VALUE"
```

### Change Styling

Modify the `<style>` section in `docs/index.html`

### Add More Fields

Add new form groups in the HTML and include them in the API request body.

## 🐛 Troubleshooting

### "Failed to trigger workflow"

**Check:**
1. Token has `workflow` scope
2. Repository owner/name is correct
3. Workflow file exists: `.github/workflows/x402-settlement-demo.yml`
4. Branch name is correct (default: `main`)

### "Token doesn't have access"

**Solution:** 
- Regenerate token with correct scopes
- Ensure token has access to the repository

### "Workflow not found"

**Solution:**
- Verify workflow file path is exactly: `.github/workflows/x402-settlement-demo.yml`
- Check the file exists in your repository

## 📱 Mobile Responsive

The interface is fully responsive and works on:
- 📱 Mobile phones
- 📱 Tablets
- 💻 Desktops

## 🔄 Updates

To update the interface:

1. Edit `docs/index.html`
2. Commit and push
3. GitHub Pages auto-deploys (1-2 minutes)

## 📊 Monitoring

After triggering:
- View workflow: `https://github.com/OWNER/REPO/actions`
- Check issue comments for settlement status
- Monitor transaction on Monad explorer

## 🎨 Customization Examples

### Change Color Scheme

```css
background: linear-gradient(135deg, #YOUR_COLOR_1 0%, #YOUR_COLOR_2 100%);
```

### Add Logo

```html
<div class="header">
    <img src="logo.png" alt="Logo" style="width: 60px; margin-bottom: 10px;">
    <h1>🚀 x402 Settlement</h1>
</div>
```

### Add More Networks

```html
<select id="network" required>
    <option value="monad-testnet">Monad Testnet</option>
    <option value="monad-mainnet">Monad Mainnet</option>
    <option value="custom">Custom Network</option>
</select>
```

## 🚨 Important Notes

- **Never commit tokens to git**
- **Test on testnet first**
- **Keep private keys secure**
- **Monitor gas costs**

## 📚 Related Documentation

- [QUICKSTART.md](../caller-repo-template/docs/QUICKSTART.md) - Full setup guide
- [MAINTAINER_GUIDE.md](../caller-repo-template/MAINTAINER_GUIDE.md) - Maintainer commands
- [x402-settlement-demo.yml](../.github/workflows/x402-settlement-demo.yml) - Workflow being triggered

---

**Status:** Production Ready ✅  
**Type:** Static Web App  
**Hosting:** GitHub Pages  
**API:** GitHub REST API v3
