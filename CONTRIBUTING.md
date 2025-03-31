## Contributing Guidelines

We welcome contributions to improve this project. Please follow these guidelines to ensure a smooth contribution process.

### Code of Conduct
The Code of Conduct for this project will be available soon. Once available, please make sure to review and adhere to it. 

### Reporting Bugs
To report bugs, please follow these steps:

1. **Search Existing Issues:** Before reporting a bug, check the [Issues](https://github.com/swarmauri/swarmauri-sdk/issues) to see if the problem has already been reported or is being addressed.
   
2. **Create a New Bug Report:** If no issue matches, open a new issue using the provided bug report template. Include:
   - Detailed steps to reproduce the bug.
   - The expected and actual behavior.
   - Screenshots, logs, or other helpful information.

### Suggesting New Features
If you have an idea for a new feature, please:

1. **Search Existing Issues:** Review existing issues to see if the feature has already been requested.

2. **Submit a New Feature Request:** If not, create a new issue using the feature request template. Provide:
   - A clear description of the feature.
   - Its potential use cases and benefits to the project.

### Suggesting Enhancements
To suggest improvements to existing features:

1. **Search Existing Issues:** Make sure the enhancement hasn’t already been proposed.

2. **Create an Enhancement Request:** If not, submit an issue with the enhancement request template. Describe:
   - The current functionality.
   - The proposed improvements and how they enhance the project.

### Style Guide
_This section is currently under development and will provide coding style conventions for the project soon._

### How to Contribute

1. **Fork the Repository:**
   - Navigate to the [repository](https://github.com/swarmauri/swarmauri-sdk) and fork it to your GitHub account.
   
2. **Star and Watch:**
   - Star the repo and watch for updates to stay informed.

3. **Clone Your Fork:**
   - Clone your fork to your local machine:  
     `git clone https://github.com/your-username/swarmauri-sdk.git`

4. **Create a New Branch:**
   - Create a feature branch to work on:  
     `git checkout -b feature/your-feature-name`

5. **Make Changes:**
   - Implement your changes. Write meaningful and clear commit messages.
   - Stage and commit your changes:  
     `git add .`  
     `git commit -m "Add a meaningful commit message"`

6. **Push to Your Fork:**
   - Push your branch to your fork:  
     `git push origin feature/your-feature-name`

7. **Write Tests:**  
   - Ensure each new feature has an associated test file.
   - Tests should cover:
     1. **Component Type:** Verify the component is of the expected type.
     2. **Resource Handling:** Validate inputs/outputs and dependencies.
     3. **Serialization:** Ensure data is properly serialized and deserialized.
     4. **Access Method:** Test component accessibility within the system.
     5. **Functionality:** Confirm the feature meets the project requirements.

8. **Create a Pull Request:**  
   - Once your changes are ready, create a pull request (PR) to merge your branch into the main repository. 
   - Provide a detailed description, link to related issues, and request a review.

### Development Setup

1. **Run Tests with GitHub Actions:**
   - GitHub Actions will automatically run tests for your changes. 
   - Check the Actions tab to verify if your changes pass the tests.

2. **Enabling GitHub Actions on Your Fork:**
   - **Check for Workflow Files:** Ensure `.yml` workflow files are present under `.github/workflows` in your fork.
   - **Enable Actions:** 
     - Go to the "**Settings**" tab of your fork.
     - Under "**Actions**" in the left sidebar, ensure Actions are enabled. If not, enable them.

### Licensing
This project is licensed under the [Project License](https://github.com/swarmauri/swarmauri-sdk/blob/master/LICENSE).  
Please ensure that your contributions comply with the terms of the license.
