# Contributing Guidelines

We welcome contributions to improve Swarmakit. This guide outlines the steps to follow when contributing, adhering to the feature-based branching principle, which helps keep the codebase clean and organized.

## Reporting Bugs

If you found an issue and you want to report it, please follow these steps:

1. **Search Existing Issues**: Before reporting a bug, check the Issues to see if the problem has already been reported or is being addressed.

2. **Create a new Bug report:** If no issue matches, open a new issue using the provided bug report template. Include:
   - Detailed steps to reproduce the bug.
   - The expected and actual behavior.
   - Screenshots, logs, or other helpful information.
  
## Suggesting New Features

If you have an idea for a new feature, please:

1. **Search Existing Features:** Review existing issues to see if the feature has already been requested.

2. **Submit a New Feature Request:** If not, create a new issue using the feature request template. Provide:
   - A clear description of the feature.
   - Its potential use cases and benefits to the project.

## Suggesting Enhancements

To suggest improvements to existing features:

1. **Search Existing Issues:** Make sure the enhancement hasn’t already been proposed.

2. **Create an Enhancement Request:** If not, submit an issue with the enhancement request template. Describe:
   - The current functionality.
   - The proposed improvements and how they enhance the project.

## How to Contribute

1. **Fork The Repository:**

    Start by creating your own copy of the Swarmakit repository:

   - Navigate to the [Swarmakit repository](https://github.com/swarmauri/swarmakit)
   - Click the Fork button in the upper right corner to create a personal copy under your GitHub account.

2. **Clone Your Forked Repository:**
  
   Once you've forked the repository, clone it to your local machine:

   ```bash
   git clone https://github.com/<your-username>/swarmakit.git
   cd swarmakit
   ```
  
   Replace `<your-username>` with your GitHub username.

3. **Set Up Your Development Environment:**

   - Ensure you have Node.js and npm installed.
   - Install dependencies
  
        ```bash
        npm install
        ```

4. **Navigate to Your Desired Library:**
  
   - Change into the directory you want to work on. For example:

        ```bash
        cd libs/vue
        ```

   - Replace `vue` with `react` or `svelte` as needed.

5. **Create a New Feature Branch:**
  
   - Before making any changes to the codebase, create a new branch of your feature:
  
        ```bash
        git checkout -b feature/<your-feature-name>
        ```  

   - Replace `<your-feature-name>` with a descriptive name for the feature you’re implementing. This naming convention helps identify the purpose of the branch.

6. **Pull the Latest Changes:**

   - Before making any modifications, ensure your local repository is up to date with the latest changes from GitHub:
  
        ```bash
        git pull 
        ```

   - This command ensures you have the latest code before starting your work.

7. **Make Your Changes:**
  
   - With your new branch created and the library selected, implement your changes:
  
     - Ensure your code follows existing coding standards.
     - Write clear, concise commit messages describing your changes.
     - Consider adding tests or documentation if applicable.

8. **Test Your Changes:**

   - Run the build command to check for any errors:

        ``` bash
        npm run build
        ```

   - If you’ve added new features, ensure they work correctly by testing manually where necessary.

9. **Commit Your Changes:**

   - Once you are satisfied with your changes, commit them to your feature branch:
  
        ```bash
        git commit -m "feat: add new component to Vue library for improved user interface"      
        ```

   - Follow the conventional commit format for commit messages, starting with feat: for new features, fix: for bug fixes, and other relevant prefixes.

10. **Push Your Changes:**

    - After committing, push your changes to your forked repository:

        ```bash
        git push origin feature/<your-feature-name>
        ```

11. **Write Tests:**
  
    - Ensure each new feature has an associated test file.
    - Tests should cover:
      1. **Component Type:** Verify the component is of the expected type.
      2. **Resource Handling:** Validate inputs/outputs and dependencies.
      3. **Serialization:** Ensure data is properly serialized and deserialized.
      4. **Access Method:** Test component accessibility within the system.
      5. **Functionality:** Confirm the feature meets the project requirements.

12. **Open a Pull Request:**

    - Navigate back to the original Swarmakit repository on GitHub:

        - Click the Pull Requests tab.
        - Click the New Pull Request button.
        - Select your feature branch from the dropdown menu and provide a clear title and description for your pull request, explaining the changes made and their purpose.
        - Click Create Pull Request.

13. **Review and Address Feedback:**

    - After submitting your pull request, maintainers will review your changes. Be open to feedback:
    - 
      - Make any requested changes by committing them to your feature branch.
      - Push the updates, and the pull request will automatically update.

14. **Merge and Celebrate:**
  
    - Keep Your Branch Updated: Regularly pull updates from the main repository to keep your feature branch up to date:

      - Once your pull request is approved, it will be merged into the main branch. Congratulations on contributing to Swarmakit!

### Development Setup

1. **Run Tests with GitHub Actions:**

   - GitHub Actions will automatically run tests for your changes. 
   - Check the Actions tab to verify if your changes pass the tests.

2. **Enabling GitHub Actions on Your Fork:**

   - **Check for Workflow Files:** Ensure `.yml` workflow files are present under `.github/workflows` in your fork.
   - **Enable Actions:**
     - Go to the "**Settings**" tab of your fork.
     - Under "**Actions**" in the left sidebar, ensure Actions are enabled. If not, enable them.

## Licensing

This project is licensed under the [Project License](https://github.com/swarmauri/swarmakit/blob/master/LICENSE).  
Please ensure that your contributions comply with the terms of the license.
