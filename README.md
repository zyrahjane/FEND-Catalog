# FEND-Catalog

## Objective: 
In this project, you will be developing a web application that provides a list of items within a variety of categories and integrate third party user registration and authentication. Authenticated users should have the ability to post, edit, and delete their own items.
You will be creating this project essentially from scratch, no templates have been provided for you. This means that you have free reign over the HTML, the CSS, and the files that include the application itself utilizing Flask.

## Instructions

### 1 Git

If you don't already have Git installed, [download Git from git-scm.com.](http://git-scm.com/downloads) Install the version for your operating system.

On Windows, Git will provide you with a Unix-style terminal and shell (Git Bash).  
(On Mac or Linux systems you can use the regular terminal program.)

You will need Git to install the configuration for the VM. If you'd like to learn more about Git, [take a look at our course about Git and Github](http://www.udacity.com/course/ud775).

### 2 VirtualBox

VirtualBox is the software that actually runs the VM. [You can download it from virtualbox.org, here.](https://www.virtualbox.org/wiki/Downloads)  Install the *platform package* for your operating system.  You do not need the extension pack or the SDK. You do not need to launch VirtualBox after installing it.

**Ubuntu 14.04 Note:** If you are running Ubuntu 14.04, install VirtualBox using the Ubuntu Software Center, not the virtualbox.org web site. Due to a [reported bug](http://ubuntuforums.org/showthread.php?t=2227131), installing VirtualBox from the site may uninstall other software you need.

### 3 Vagrant

Vagrant is the software that configures the VM and lets you share files between your host computer and the VM's filesystem.  [You can download it from vagrantup.com.](https://www.vagrantup.com/downloads) Install the version for your operating system.

### 4 Running the Catalog project
Once in catalog directory, type **vagrant ssh**. This will log your terminal into the virtual machine, and you'll get a Linux shell prompt. When you want to log out, type **exit** at the shell prompt.  To turn the virtual machine off (without deleting anything), type **vagrant halt**. If you do this, you'll need to run **vagrant up** again before you can log into it.


Now that you have Vagrant up and running type **vagrant ssh** to log into your VM.  change to the /vagrant directory by typing **cd /vagrant**. This will take you to the shared folder between your virtual machine and host machine.

Type **ls** to ensure that you are inside the directory that contains project.py, database_setup.py, and two directories named 'templates' and 'static'

Now type **python database_setup_zb.py** to initialize the database.

Type **python lotsofcocktails.py** to populate the database with the alcoholic bases and coctail items. (Optional)

Type **python application.py** to run the Flask web server. In your browser visit **http://localhost:5000** to view.

### 4 Logging on with Facebook

Must register app here https://developers.facebook.com/. Add a 'Facebook Login'. With http://localhost:5000/ to the Valid OAuth redirect URIs section. Copy and paste App ID and App secret to App Secret to the fb_client_secrets.json file. Also add to App ID to login.html on line 78.

### 5 Logging on with Gmail 

Must register app here https://console.developers.google.com/apis. Choose Credentials from the menu on the left. Create an OAuth Client ID. When you're presented with a list of application types, choose Web application. Set the authorized JavaScript origins http://localhost:5000/. Download JSON, rename to client_secrets.json and move to directory. Clientid must be replaced on line 24 of login.html.
