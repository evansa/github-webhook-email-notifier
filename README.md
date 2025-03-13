# GitHub Webhook Email Notifier

This project is a Flask application that receives GitHub webhook events and sends email notifications when GitHub Actions workflows fail.

## Features

- Receives webhook events from GitHub
- Authenticates webhooks using GitHub's signature verification
- Sends email notifications when workflows fail
- Runs in Docker for easy deployment

## Setup Instructions

### 1. Clone this repository

```bash
git clone https://github.com/evansa/github-webhook-email-notifier.git
cd github-webhook-email-notifier
```

### 2. Configure environment variables

Copy the example environment file and modify it with your settings:

```bash
cp .env.example .env
```

Edit the `.env` file with your actual values:

- `GITHUB_WEBHOOK_SECRET`: A secret string that you'll also configure in GitHub
- `SMTP_SERVER`: Your email server (e.g., smtp.gmail.com)
- `SMTP_PORT`: Your email server port (e.g., 587 for TLS)
- `SMTP_USERNAME`: Your email username
- `SMTP_PASSWORD`: Your email password or app password
- `SENDER_EMAIL`: The email address that will send notifications
- `RECIPIENT_EMAIL`: The email address that will receive notifications

**Note for Gmail users**: You'll need to use an "App Password" instead of your regular password. See [Google's documentation](https://support.google.com/accounts/answer/185833) for details.

### 3. Build and run with Docker

```bash
docker-compose up --build -d
```

This will start the webhook service on port 5000 (or the port you specified in the .env file).

### 4. Make the webhook accessible from the internet

To receive webhooks from GitHub, your server needs to be accessible from the internet. You can:

- Deploy to a cloud provider
- Use a service like ngrok for development: `ngrok http 5000`

### 5. Configure the webhook in GitHub

1. Go to your GitHub repository
2. Click Settings → Webhooks → Add webhook
3. Set the Payload URL to your server's URL + /webhook (e.g., `https://your-server.com/webhook`)
4. Set Content type to `application/json`
5. Set the Secret to the same value as `GITHUB_WEBHOOK_SECRET` in your .env file
6. Under "Which events would you like to trigger this webhook?", select "Workflow runs"
7. Ensure "Active" is checked
8. Click "Add webhook"

### 6. Modify your GitHub Actions workflow

Add the following step to your GitHub Actions workflow:

```yaml
- name: Send Notification on Failure
  if: ${{ failure() }}
  uses: actions/github-script@v6
  with:
    script: |
      const workflow_run = {
        conclusion: 'failure',
        name: context.workflow,
        html_url: `https://github.com/${context.repo.owner}/${context.repo.repo}/actions/runs/${context.runId}`
      };
      
      await github.rest.repos.createDispatchEvent({
        owner: context.repo.owner,
        repo: context.repo.repo,
        event_type: 'workflow_run',
        client_payload: {
          workflow_run: workflow_run,
          repository: {
            full_name: `${context.repo.owner}/${context.repo.repo}`
          },
          action: 'completed'
        }
      });
```

## Security Considerations

- Keep your `GITHUB_WEBHOOK_SECRET` secure
- Consider using HTTPS for your webhook server
- The webhook verifies that requests are coming from GitHub using the secret signature

## Troubleshooting

- Check logs: `docker-compose logs`
- Verify your environmental variables are set correctly
- Ensure your SMTP settings are correct and the account can send emails
- Make sure your webhook is reachable from the internet