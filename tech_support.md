---
layout: page
title: 🙋‍♂️ Tech Support
description: Pointers on how to solve common technical issues.
nav_order: 4
---

# 🙋‍♂️ Tech Support
{:.no_toc}

## Table of contents
{: .no_toc .text-delta}

1. TOC
{:toc}

---

## Introduction

In the real world, you'll be expected to set up and maintain a Python
environment locally – that is, on your own computer – and so that's what we'll
have you do in this course as well.

There has been a lot written about how to set up a Python environment, so we
won't reinvent the wheel. This page will only be a summary; Google will be your
main resource. But always feel free to come to a staff member's office hours if
you have a question about setting up your environment, using Git, or similar —
we're here to help.

## Environments and Package Managers

For this class, the software you'll need includes Python 3.12, `uv`, a few
specific Python packages, Git, and a text editor.

Gradescope has an **environment** which it uses to autograde your work. You can
think of an environment as a combination of a Python version and _specific_
versions of Python packages that is isolated from the rest of your computer. In
practice, developers create different environments for different projects, so
that they can use different versions of packages in different projects.

We're going to have you replicate the environment Gradescope has on your
computer. The reason for this is so that your code behaves the same when you
submit it to Gradescope as it does when you work on it on your computer. For
example, our Gradescope environment uses `numpy` version `2.1.1`; if you install
a different version of `numpy` on your computer, for example, you might see
different results than Gradescope sees.

How do you install packages, then? `pip` is a common choice, but even though
it's widely used, it lacks built-in support for creating isolated environments.
This limitation makes it challenging to maintain version consistency and avoid
conflicts between packages. **Consequently, we do not recommend using `pip` at
all for environment management**, as it may inadvertently introduce incompatible
package versions.

[`uv`][uv], on the other hand, is a powerful tool that not only installs
packages but also manages environments effortlessly. It allows you to create
isolated environments and ensures compatibility among the packages within those
environments.

[uv]: https://docs.astral.sh/uv/

---

## Replicating the Gradescope Environment

Below, we're going to walk you through how to create the same environment that
Gradescope uses.

### Step 0 (Windows only): Windows Subsystem for Linux

{: .yellow}

> You can skip this step if you are not using a Windows machine, or if you
> already have WSL set up.

If you are using a Windows machine, we will use the Windows Subsystem for Linux
(WSL) to give you a Linux terminal. This isn't absolutely necessary to follow
along with the course, but it will make the rest of the setup much easier. We
will not support or document other setups for the course.

1. Open PowerShell and run:

   ```bash
   wsl --install
   ```

   This will install the latest version of Ubuntu.

   For more details, see the [Microsoft documentation][wsl].

   [wsl]: https://learn.microsoft.com/en-us/windows/wsl/setup/environment

1. Now, launch the Ubuntu terminal by making a new tab in the Windows Terminal
   and selecting "Ubuntu" from the dropdown, or by going to your Start Menu and
   opening "Ubuntu". Ubuntu is a Linux distribution that is installed by default
   with WSL.

1. Now, install `git`. In your Ubuntu terminal, run:

   ```bash
   sudo apt-get update
   sudo apt-get install git
   ```

   For more details, see the [Git documentation for WSL][gitwsl].

   [gitwsl]: https://learn.microsoft.com/en-us/windows/wsl/tutorials/wsl-git

{: .yellow}

> All future setup steps will assume you are either using the Ubuntu, macOS, or
> Linux terminal.

### Step 1: Install `uv`

Run the `uv` installer. To do this, open your Terminal and run:

```
curl -LsSf https://astral.sh/uv/install.sh | sh
```

After this step, check that `uv` is available by running the `uv` command. If
this command doesn't work, you may need to start a new terminal window and close
your old one.

```
$ uv
An extremely fast Python package manager.

Usage: uv [OPTIONS] <COMMAND>

...
```

You should see a help menu listing the available commands.

### Step 2: Clone the course repository

Clone the course GitHub repository, which not only contains the course
materials, but also a `pyproject.toml` file with the necessary details
to configure your environment:

```bash
git clone {{ site.urls.github }}
```

This will create a folder called `{{ site.urls.github | split: '/' | last }}`.
If you look at the
`pyproject.toml` file inside, you'll see that it contains a specific Python
version (`python=3.12`) along with specific package versions (like
`pandas==2.2.3` and `requests==2.32.3`, for example).

### Step 3: Sync the environment

To sync the environment, navigate to the cloned repository folder (`cd {{
site.urls.github | split: '/' | last }}`), then in your Terminal, run:

```
uv sync
```

You should see that `uv` will download and install the packages we need for the
course.

### Step 4: Check that everything is working

To check that everything is working, you can run the following command in your Terminal:

```bash
uv run otter --version
# should print info about the Python version, and display a line showing that the
# otter-grader version is 3.1.4
```

---

## Working on Assignments

The setup instructions above only need to be run once.

Now, you can open Jupyter Lab, by using the `uv run jupyter lab` command in your
Terminal. You can also use VSCode to open notebooks by setting the Python interpreter to the one installed
by `uv`.

### Using Git

All of our course materials, including your assignments, are hosted on GitHub in
[this Git repository]({{ site.urls.github }}).

Git is a _version control system_. In short, it is used to keep track of
the history of a project. With Git, you can go back in time to any
previous version of your project, or even work on two different versions
(or \"branches\") in parallel and \"merge\" them together at some point
in the future. We\'ll stick to using the basic features of Git in this course.

There are Git GUIs, and you can use them for this class. You can also use the
command-line version of Git. We've already used `git` above to clone the course
repository.

Moving forward, to bring in the latest version of the repository, in your local
repository, run:

```
git pull
```

This will **not** overwrite your work. In fact, Git is designed to make it very
difficult to lose work (although it\'s still possible!).

**Merge Conflicts**

You might face issues when using `git pull` regarding merge issues and branches.
This is caused by files being updated on your side while we are also changing
the Git repository by pushing new assignments on our side. Here are some steps
you can follow to resolve them:

NOTE: Whenever working with GitHub pulls, merges, etc., it's a good idea to save
your important work locally so that if you accidentally overwrite your files you
still have the work saved. **Save your work locally before following the steps
below.**

1. `git status` shows the current state of your Git working directory and
   staging area. It's a good sanity check to start with. You will probably see
   your project and lab files that you have worked on.
2. `git add .` will add all your files to be ready to commit.
3. `git commit -m "some message of your choice"` will commit the files, with
   some description in the quotations. This can be whatever you want, it won't
   matter.

At this stage, if you `git pull`, it should work. You should double-check that
you have new files, as well as that your old files are unchanged. If they are
changed then you should be able to just copy-paste from your local backup. If
this does **not** work then you may have **merge conflicts**, follow the next
steps:

4. `git checkout --ours [FILENAME]` will tell git that whenever a conflict
   occurs in `[FILENAME]` to keep your version. Run this for each file with a
   conflict.
5. `git add [FILENAME]` to mark each file with a conflict as resolved.
6. `git commit` to commit the changes.

### Choosing a Text Editor or IDE

In this class, you will need to use a combination of editors for doing
your assignments: The Python files should be developed with a text editor (for
syntax highlighting and running doctests) and the data/results should be
analyzed/presented in Jupyter Notebooks. Below is an incomplete list of
IDEs you might want to try. For more information about them, feel free
to ask the course staff.

If you're curious, the course instructor uses VSCode to edit .py files and the
JupyterLab environment to edit notebooks.

- The [JupyterLab](https://jupyterlab.readthedocs.io/en/stable/) text
  editor: see [below](#jupyterlab). Can be used to edit both notebooks and .py files.

- [VSCode](https://code.visualstudio.com/): Microsoft Visual Studio Code.
  Currently very popular, and can also be used to edit both notebooks and .py
  files.

- [sublime](https://www.sublimetext.com/): A favorite text editor of
  hackers, famous for its multiple cursors. A good, general-purpose
  choice.

- [PyCharm (IntelliJ)](https://www.jetbrains.com/pycharm/): Those who
  feel at home coding Java. Can only work locally.

- [(neo)vim](https://neovim.io/): lightweight, productive text-editor
  that runs in the terminal. Very popular among developers, but also has a very
  steep learning curve.

### Using VSCode to Run Jupyter Notebooks

Many students like to use VSCode to edit Jupyter Notebooks. If that's you, then you'll need to make sure
to activate your environment within your notebook in VSCode. Here's how to do that.

1. Open a Juypter Notebook in VSCode.
1. Click "Select Kernel" in the top right corner of the window.
<center><img src="../assets/images/ts-select-kernel.png" width=150></center>
1. Click "Python: Select Interpreter" in the toolbar that appears in the middle.
<center><img src="../assets/images/ts-python-environments.png" width=300></center>
1. Finally, click ".venv (Python 3.13.2)".
<!-- <center><img src="../assets/images/ts-dsc80-conda.png" width=500></center> -->

<!-- ## Working Remotely via DataHub

Working *remotely* means using an environment that someone else set up
for you on a computer far, far away, usually through the browser. This
is the way you wrote code in DSC 10, for instance. There\'s nothing
wrong with this, *per se*, and it is simpler, but you should think of
this option as developing with \"training wheels\". Eventually, you will
need to learn how to set up your own Python environment, and now is as
good a time as any.

There are servers available to use at
[datahub.ucsd.edu](datahub.ucsd.edu). These are a lot like the
DataHub servers that you used in DSC 10, however they are customized
for this course. After logging in with your UCSD account, you will be
taken the familiar juptyer landing page. The server you are logged into
has \~4GB of RAM available, and has Python with all the necessary
packages.

### ⚠️ Warning!

DataHub outages are not uncommon, and they can be expected to occur once
or twice per quarter (sometimes more). Outages typically last for a few
hours or less, but they can prevent you from working on your assignment.

Since we do not manage DataHub, we cannot make any guarantees about its
availability. DataHub crashes that prevent you from turning in or
working on your assignment near the deadline are typically handled via
the usual [slip day](../syllabus) mechanism. If DataHub
has been down for a long time (more than 24 hours), let us know and
we\'ll consider a blanket extension -- though this has very rarely
(never?) happened.

Our advice is to use a local development environment, or to at least
have one as available as a backup option. If you decide to use DataHub
as your first choice, you should keep an extra slip day or two in
reserve in case the server crashes.

### Installing or Updating Python Packages

To update a package (e.g. `pandas`) on DataHub, you\'ll need to use the
command line. To do this, open "New \> Terminal" and type:

`mamba install --user --upgrade pandas`

followed by the enter key to run the command.

One package that you\'ll likely need to install is `otter-grader`. This
package provides the autograder that checks your answers in the labs and
projects.

### JupyterLab

The remote servers have a development environment installed on them,
however, it's non-intuitive how to access it. Once on the landing page,
the url should read something like:

`https://datahub.ucsd.edu/user/USER/tree`

You can access the IDE (integrate development environment) by changing
\"tree\" to \"lab\". This brings up JupyterLab. The url should look
something like this:

`https://datahub.ucsd.edu/user/USER/lab`

For more information on this IDE, you can see read about it here. From
within JupyterLab, you can:

-   Use a Python console
-   Run Jupyter notebooks
-   Use a terminal (e.g. to pull git repos)
-   Develop Python code in .py files

### Git

Whether you work locally or use DataHub, you'll need to pull assignments from GitHub. If you work on DataHub, you'll **have** to pull from GitHub using the command-line. To do this, open "New \> Terminal" and, to get the course repository for the first time, type:

    git clone https://github.com/dsc-courses/dsc80-2023-fa

Then, open up the file-tree in the original Jupyter tab, and you should see all the
course files now there. If you have already cloned the repository, and
just want to get the latest files, type `git pull` and you should see
the updated files.

### Troubleshooting DataHub

**What if I accidentally clicked a different class instead of DSC 80 when logging into DataHub, or what if my DataHub doesn't load?**

1. If you are already logged into DataHub, click "Control Panel" in the top right. (If your DataHub never launched in the first place, proceed to the next step.)

2. In the toolbar at appears at [datahub.ucsd.edu](https://datahub.ucsd.edu), click "Services" then click "manual-resetter", then click "Reset". If a pop-up box appears, that's okay.

3. Log back into DataHub again and it should allow you to select a course – select DSC 80. -->
