# Brew Mirror Automation

This project automates the process of mirroring Homebrew repositories and storing them in S3 using AWS Lambda, scheduled weekly by GitHub Actions.

## Features
- Mirrors Homebrew taps and bottles to S3.
- Mirrors additional repositories (`brew`, `install`, `homebrew-services`, and `homebrew-portable-ruby`).
- Stores each mirror run with a timestamped folder in S3.
- Triggered by GitHub Actions on a weekly basis.
- Handles hash comparison to avoid duplicate downloads.

## Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-repo/brew-mirror-automation.git
   cd brew-mirror-automation```

2. **Set up AWS credentials**:
Go to your repository settings on GitHub.
Under `Settings > Secrets > Actions`, add the following secrets:
`WS_ACCESS_KEY_ID`
`AWS_SECRET_ACCESS_KEY`

3. **Run OpenTofu to create the infrastructure**:
Ensure you have OpenTofu installed.
Apply the infrastructure using the following command:
   ```bash
opentofu init
opentofu apply
This will set up the necessary AWS infrastructure, including the S3 bucket, Lambda function, and necessary permissions.
```

# How to Use

## Lambda Function
The Lambda function is responsible for mirroring Homebrew repositories and storing them in S3. 
The function performs the following:
Freezes the current Homebrew `tap` state to avoid issues caused by repository updates during the mirroring process.
Downloads bottles and specified repositories (`brew`, `install`, `homebrew-services`, and `homebrew-portable-ruby`).
Uploads the downloaded files to S3, storing each run in a timestamped folder.
Compares the current hash of each bottle to the previous run to avoid downloading bottles that have already been mirrored.
You can modify the Lambda function in `lambda/lambda_function.py` to customize behavior (e.g., add additional repositories or modify download logic).

# S3 Storage

## All mirrored files are stored in S3 in the following structure:

   ```bash
brew-mirror-bucket/
├── mirrors/
│   ├── YYYY-MM-DD_HH-MM-SS/
│   │   ├── brew.zip
│   │   ├── install.zip
│   │   ├── homebrew-services.zip
│   │   ├── portable-ruby/
│   │   └── bottles/
│   │       ├── bottle1.tar.gz
│   │       └── bottle2.tar.gz
│   └── latest/
│       └── downloaded-hashes.txt
```

Each mirror run is stored in a folder named with a timestamp (e.g., `2024-10-22_14-30-00`).
The `latest` folder contains the most recent `downloaded-hashes.txt` file for reference in future runs.

## Triggering the Lambda Function
The Lambda function is automatically triggered every week using GitHub Actions.
To manually trigger the Lambda function, you can use the `workflow_dispatch` option in the GitHub Actions interface.

## GitHub Actions
GitHub Actions runs the mirroring process on a weekly schedule. It:
Invokes the AWS Lambda function.
Logs the process for easy monitoring.
To manually run the process, navigate to the "Actions" tab in your GitHub repository, select the relevant workflow, and click "Run workflow".

## Monitoring
AWS CloudWatch is used to monitor the Lambda function. You can access the logs by navigating to CloudWatch in your AWS console and reviewing the logs for the `brew-mirror-lambda` function.
S3: You can verify that the files are being uploaded correctly by checking the S3 bucket for the timestamped folders and files.

## Additional Notes
Ensure that the necessary permissions are granted to the Lambda function, including access to S3 and GitHub repositories.
You can customize the repositories to mirror by modifying the list of repositories in the Lambda function.

## Troubleshooting
No files in S3: Check CloudWatch logs to ensure that the Lambda function ran successfully and that it has the correct permissions to upload files to S3.
GitHub Actions errors: Check the logs in the "Actions" tab of your repository to diagnose any issues with the scheduled jobs.

