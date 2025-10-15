# AI-Freelance-Contracts-Checker

[![AWS](https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![Bedrock](https://img.shields.io/badge/Amazon_Bedrock-FF9900?style=for-the-badge&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/bedrock/)

<a id=""></a>


## **Contents**

- [🎯 Overview `⇧`](#overview-)
- [🌟 Features `⇧`](#features-)
- [🏗️ Architecture `⇧`](#architecture-)
- [🛠️ Environment setup `⇧`](#environment-setup-)
- [🧩 Project Structure `⇧`](#project-structure-)
- [👥 Contributors `⇧`](#contributors-)

<a id="overview-"></a>

# 🎯 Overview [`⇧`](#contents)


<a id="features-"></a>

# 🌟 Features [`⇧`](#contents)

<a id="architecture-"></a>

# 🏗️ Architecture [`⇧`](#contents)

![Architecture Diagram](architecture.png)



### AgentCore Runtime


### Knowledge Management

### Memory System

### Key AWS Services Used

* **Amazon CloudFront**: Content delivery network
* **S3**: Object storage for static website and knowledge base
* **API Gateway**: RESTful API management
* **Lambda Functions**: Serverless compute for OCR and orchestration
* **Amazon Bedrock**: Managed AI/ML foundation models
* **Guardrails**: AI safety and compliance controls


##  Live Demo [`⇧`](#contents)

- **Website**: [http://egyptian-legal-analysis-ui.s3-website-us-west-2.amazonaws.com/](https://egyptian-legal-analysis-ui.s3.amazonaws.com/index.html)


<a id="environment-setup"></a>

# Environment setup [`⇧`](#contents)
1. First and foremost, please see the suggested IDE setup in the dropdown below to make sure that your editor is ready for development.

> [!IMPORTANT]
>
> <details><summary>Suggested IDE setup</summary>
>
> <p>
>
> VS Code
>
> Install the following extensions:
>
> - [charliermarsh.ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)
> - [streetsidesoftware.code-spell-checker](https://marketplace.visualstudio.com/items?itemName=streetsidesoftware.code-spell-checker)
>
> </p>
> </details>

1. [Fork](https://docs.github.com/en/get-started/quickstart/fork-a-repo) the [AI-Legal-Checker repo](https://github.com/activist-org/AI-Legal-Checker), clone your fork, and configure the remotes:

> [!NOTE]
>
> <details><summary>Consider using SSH</summary>
>
> <p>
>
> Alternatively to using HTTPS as in the instructions below, consider SSH to interact with GitHub from the terminal. SSH allows you to connect without a user-pass authentication flow.
>
> To run git commands with SSH, remember then to substitute the HTTPS URL, `https://github.com/...`, with the SSH one, `git@github.com:...`.
>
> - e.g. Cloning now becomes `git clone git@github.com:<your-username>/AI-Legal-Checker.git`
>
> GitHub also has their documentation on how to [Generate a new SSH key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent) 🔑
>
> </p>
> </details>

```bash
# Clone your fork of the repo into the current directory.
git clone https://github.com/OmarAI2003/AI-Freelance-Contracts-Checker
# Navigate to the newly cloned directory.
cd AI-Freelance-Contracts-Checker
# Assign the original repo to a remote called "upstream".
git remote add upstream https://github.com/OmarAI2003/AI-Freelance-Contracts-Checker
```

- Now, if you run `git remote -v` you should see two remote repositories named:
  - `origin` (forked repository)
  - `upstream` (AI-Freelance-Contracts-Checker repository)

3. Create a virtual environment, activate it and install dependencies:

   ```bash
   # Unix or MacOS:
   python3 -m venv venv
   source venv/bin/activate

   # Windows:
   python -m venv venv
   venv\Scripts\activate.bat

   # After activating venv:
   pip install --upgrade pip
   pip install -r requirements-dev.txt

   # To install the AI-Freelance-Contracts-Checker for local development:
   pip install -e .
   ```

You're now ready to work on `AI-Freelance-Contracts-Checker`!


## 🆘 Support

For issues and questions:
1. Check the docs/ folder for detailed documentation
2. Review CloudWatch logs for debugging
3. Ensure all AWS services are properly configured
4. Verify agent deployment status

<a id="project-structure-"></a>

# 📁 Project Structure [`⇧`](#contents)
```
AI-Freelance-Contracts-Checker/
├── src/
│   └── __init__.py
├── data/
│   └── contracts/
|   └── .gitkeep
├── tests/
│   └── __init__.py
├── .gitignore
├── README.md
├── requirements.txt
├── requirements-dev.txt
└── architecture.md
└── README.md

```

## 📄 License 

This project is licensed under the MIT License - see the LICENSE file for details.

<a id="contributors-"></a>

# Contributors [`⇧`](#contents)

Thanks to all our amazing contributors! ❤️

<a href="https://github.com/mustafatawfiq">
  <img src="https://avatars.githubusercontent.com/mustafatawfiq" width="50" height="50" style="border-radius:50%" />
</a>
<a href="https://github.com/lola-16">
  <img src="https://avatars.githubusercontent.com/lola-16" width="50" height="50" style="border-radius:50%" />
</a>
<a href="https://github.com/mennamohammeddd">
  <img src="https://avatars.githubusercontent.com/mennamohammeddd" width="50" height="50" style="border-radius:50%" />
</a>
<a href="https://github.com/OmarAI2003">
  <img src="https://avatars.githubusercontent.com/OmarAI2003" width="50" height="50" style="border-radius:50%" />
</a>
