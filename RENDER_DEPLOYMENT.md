# Deploying Web Crawler to Render

This guide provides step-by-step instructions for deploying the Web Crawler project to Render, which offers a reliable free tier.

## Render Free Tier Benefits

- 750 hours of runtime per month (enough for continuous operation)
- 512 MB RAM
- 1 CPU
- Custom domains with free SSL
- Automatic deployments from GitHub
- No credit card required for free tier

## Deployment Options

There are two ways to deploy to Render:

1. **Automatic deployment** using the Render Dashboard and GitHub
2. **Blueprint deployment** using the render.yaml file (useful for team environments)

We'll cover both methods.

## Method 1: Automatic Deployment (Easiest)

### 1. Create a GitHub Repository

First, push your code to GitHub:

```bash
# Initialize a git repository if not already done
cd /Users/anupampandey/Downloads/web_crawler_project
git init
git add .
git commit -m "Initial commit"

# Create a repository on GitHub and push
git remote add origin https://github.com/YOUR_USERNAME/web-crawler-project.git
git push -u origin main
```

### 2. Connect Render to GitHub

1. Create an account at [render.com](https://render.com) (sign up with GitHub for easier connection)
2. Once logged in, click "New +" and select "Web Service"
3. Connect your GitHub account if prompted
4. Find and select your `web-crawler-project` repository

### 3. Configure Your Web Service

Fill in the following details:

- **Name**: `web-crawler-demo` (or your preferred name)
- **Environment**: `Python`
- **Region**: Choose the closest to you or your examiners
- **Branch**: `main`
- **Build Command**: `pip install -r requirements.txt && python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"`
- **Start Command**: `uvicorn api.app:app --host 0.0.0.0 --port $PORT`
- **Plan**: `Free`

Under the "Advanced" section, add these environment variables:
- `CRAWLER_DELAY` = `1.0`
- `RESPECT_ROBOTS` = `true`
- `PYTHONPATH` = `.`

### 4. Deploy Your Service

Click "Create Web Service". Render will now:
1. Clone your repository
2. Install dependencies
3. Download NLTK data
4. Start your application

The deployment will take 5-10 minutes for the first build.

### 5. Access Your Application

Once deployed, Render will provide a URL like `https://web-crawler-demo.onrender.com` where your application is accessible.

## Method 2: Blueprint Deployment (Using render.yaml)

This method uses the `render.yaml` configuration file already included in the project.

### 1. Push Code to GitHub

As in Method 1, push your code to GitHub.

### 2. Create a Blueprint Instance

1. Log in to [render.com](https://render.com)
2. Navigate to the "Blueprints" section
3. Click "New Blueprint Instance"
4. Connect your GitHub account if prompted
5. Select your `web-crawler-project` repository
6. Click "Approve"

Render will automatically detect the `render.yaml` file and create all the services defined in it.

### 3. Monitor Deployment

Render will create the services defined in the `render.yaml` file. You can monitor the deployment progress on the dashboard.

## Testing Your Deployment

Run the demo script against your deployed application:

```bash
python demo/demo_crawler.py [https://web-crawler-demo.onrender.com](https://web-crawler-project-r685.onrender.com) https://www.example.com
```

## Important Considerations

### Free Tier Limitations

- **Sleep Mode**: Free tier services will "sleep" after 15 minutes of inactivity
- **Startup Delay**: The first request after sleep will take 30-60 seconds as the service restarts
- **Monthly Limit**: 750 hours per month (enough for one service to run continuously)

### Keeping Your Service Active

For a one-time demo, the free tier is perfectly adequate, as long as you let examiners know about the potential cold start delay.

## Monitoring and Troubleshooting

### View Logs

From the Render dashboard, click on your web service, then select the "Logs" tab to view real-time logs.

### Check Service Status

The "Events" tab in your service dashboard shows deployment history and service status changes.

## Cleanup

When you no longer need the application:

1. Go to the Render dashboard
2. Select your web service
3. Click "Settings"
4. Scroll to the bottom and click "Delete Service"
