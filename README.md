# Introduction

Hi, and welcome to the source code for the St. De Paul Assistance Center.

Website: https://stdepaul.org

# Getting set up locally

1. Create a virtualenv, download the requirements from `requirements.txt`

2. Set the environment variables: STDEPAUL_SETTINGS_SECRET_KEY, IS_PRODUCTION ('False' on your local), STDEPAUL_ALLOWED_HOSTS (comma separated list (see settings.py)), STDEPAUL_AWS_KEY, STDEPAUL_AWS_SECRET, STDEPAUL_AWs_BUCKET_NAME, STDEPAUL_RECAPTCHA_KEY, STDEPAUL_RECAPTCHA_SECRET, STDEPAUL_SENDGRID_API_KEY, STDEPAUL_DBPW, STDEPAUL_POSITIONSTACK_ACCESS_KEY, and STDEPAUL_DB_NAME. `settings.py` for usage. You will need to either register credentials at each service (AWS, Google Recaptcha, etc) or write random characters. Obviously if you write random characters, those services won't work locally.

3. Migrate the database 

After doing this, you should be able to do `runserver`!

# Contributing

## Our Communities, and getting involved

 - Instagram: https://instagram.com/stdepaul

 - Discord: https://discord.gg/krEyds6Cp2

 - My LinkedIn: https://linkedin.com/in/mikejohnsonjr

## Immediate Tasks

At the moment, we need more data. At the moment, we only have data for Texas, PA, and CA, from state 211 sites. If you would like to contribute, you'd help a lot by creating scripts that get data from state 211 sites. Selenium is probably the best library for this task. If you're new to selenium, join our discord and I can guide you. Also, the scripts for Texas, CA, and PA are in `data_extract` as management commands.

When you are done getting and adding the data locally, do a dumpdata, like `python manage.py dumpdata > new_data.json --natural-foreign` (notice the `natural-foreign` -- this is so we can load the data to the production server) and put the .json file in the `data` dir, push to dev, and make a pull request. 

I thought about maybe adding a REST API function so that contributors can add data to the production server as they are getting the data, but sometimes mistakes are made, especially with selenium, so I think getting a working implementation and correct data is best before adding to the production server.

### State 211 data checklist

- [ ] Alabama
- [ ] Alaska
- [ ] Arizona
- [ ] Arkansas
- [x] California - 211ca.org
- [ ] Colorado - 211colorado.org
- [ ] Connecticut
- [ ] Delaware
- [ ] Florida
- [ ] Georgia
- [ ] Hawaii
- [ ] Idaho
- [ ] Illinois
- [ ] Indiana
- [ ] Iowa
- [ ] Kansas
- [ ] Kentucky
- [ ] Louisiana
- [ ] Maine
- [ ] Maryland
- [ ] Massachusetts
- [ ] Michigan
- [ ] Minnesota
- [ ] Mississippi
- [ ] Missouri
- [ ] Montana
- [ ] Nebraska
- [ ] Nevada
- [ ] New Hampshire
- [ ] New Jersey
- [ ] New Mexico
- [ ] New York
- [ ] North Carolina
- [ ] North Dakota
- [ ] Ohio
- [ ] Oklahoma
- [ ] Oregon
- [x] Pennsylvania - pa211.org
- [ ] Rhode Island
- [ ] South Carolina
- [ ] South Dakota
- [ ] Tennessee
- [x] Texas - 211texas.org
- [ ] Utah
- [ ] Vermont
- [ ] Virginia
- [ ] Washington
- [ ] West Virginia
- [ ] Wisconsin
- [ ] Wyoming

# To add later

 - Transportation help
 - Help applying for social services online (similar to turbotax), with virtual mailing addresses (so homeless people without addresses can apply)

### Rules

1. We will make absolutely **no** use of Artificial Intelligence / Machine Learning. 

2. We will not be making a group home database, until we have researched and concluded that group homes do not lower the quality of life of the neighbors in the neighborhood in which group homes are.

3. We do not condone people who are not licensed landlords offering free housing to people who need housing via St. De Paul. We recommend that you donate money or add housing assistance information to the wiki instead.

4. No hate speech and no politics.

# License

MIT License
