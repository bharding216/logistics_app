# Logistics Management Application

## Project Description
The purpose of this project was to create a tool that can track the bulk chemical outbound shipments for a chemical manufacturer (client). The manufacturer was previously using a spreadsheet to manage their schedule. 

There were several motivating factors for completing this project:
- To improve the security of the data by storing it in a relational database (MySQL)
- We needed an application that could live-update
- Reduce the number of emails sent (and the potential for an email to go unnoticed)
- Give structure to the data so that analysis can be performed
- Create user 'roles' and access rights to improve data integrity

Throughout this project I learned so many great skills, such as:
- how to create RESTful APIs,
- how to deploy a database to a remote server (using Heroku), 
- how to send an email based on a user action on the website, 
- how to implement user authentication and assign access rights/permissions to each user, and (most importantly) 
- how to collaborate with industry professionals and create a software product that makes their job much easier. 

## Using the Project

This project has been deployed to https://www.carbonfree.dev/. 

To use the program locally: 
1. Create a folder for the project root directory. Clone the repository to this folder. 
2. Install `virtualenv`. From the command line:
```
python3 -m pip install virtualenv
```
3. Open a terminal in the project root directory and run:
```
virtualenv env
```
4. Then execute the command (for Windows):
```
env\Scripts\activate.bat
```
5. Install the dependencies:
```
(env) python3 -m pip install -r requirements.txt
```
6. Now you are ready to run the program!

## License
MIT License

