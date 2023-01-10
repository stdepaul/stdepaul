# Introduction

Hi, and welcome to the source code for the St. De Paul Assistance Center.

Website: https://stdepaul.org

# Getting set up locally

1. Create a virtualenv, download the requirements from `requirements.txt`

2. Set the environment variables: STDEPAUL_SETTINGS_SECRET_KEY, IS_PRODUCTION ('False' on your local), STDEPAUL_ALLOWED_HOSTS (comma separated list (see settings.py)), STDEPAUL_AWS_KEY, STDEPAUL_AWS_SECRET, STDEPAUL_AWs_BUCKET_NAME, STDEPAUL_RECAPTCHA_KEY, STDEPAUL_RECAPTCHA_SECRET, STDEPAUL_SENDGRID_API_KEY, STDEPAUL_DBPW, STDEPAUL_POSITIONSTACK_ACCESS_KEY, and STDEPAUL_DB_NAME. `settings.py` for usage. You will need to either register credentials at each service (AWS, Google Recaptcha, etc) or write random characters. Obviously if you write random characters, those services won't work locally.

3. Migrate the database 

After doing this, you should be able to do `runserver`!

# Contributing

### Rules

1. We will make absolutely **no** use of Artificial Intelligence / Machine Learning. 

2. We will not be making a group home database, until we have researched and concluded that group homes do not lower the quality of life of the neighbors in the neighborhood in which group homes are.

3. We do not condone people who are not licensed landlords offering free housing to people who need housing via St. De Paul. We recommend that you donate money or add housing assistance information to the wiki instead.

4. No hate speech and no politics.

# License

MIT License

# Instagram

https://instagram.com/stdepaul

# Discord

https://discord.gg/krEyds6Cp2

# My linkedin

https://linkedin.com/in/mikejohnsonjr

# Immediate Tasks

## State 211 data checklist

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
- [x] Pennsylvania
- [ ] Rhode Island
- [ ] South Carolina
- [ ] South Dakota
- [ ] Tennessee
- [x] Texas
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