# blue-button.py
blue-button.py is a Python Blue Button client for LinuxForHealth that utilizes the CMS Blue Button 2.0 API to retrieve medicare.gov patient medical records authorized for LinuxForHealth. The Blue Button client then transmits those records to LinuxForHealth for inclusion in the longitudinal patient record.

## Pre-requisites
- [Python 3.8 or higher](https://www.python.org/downloads/mac-osx/) for runtime/coding support
- [Pipenv](https://pipenv.pypa.io) for Python dependency management  
- [Docker Compose 1.28.6 or higher](https://docs.docker.com/compose/install/) for a local container runtime

## Set up a local LinuxForHealth connect environment
Follow the instructions to clone and configure [LinuxForHealth connect](https://github.com/LinuxForHealth/connect).  Start connect and supporting services in containers:
```shell
docker-compose --profile deployment up -d
```

## Clone the LinuxForHealth Blue Button repository
Clone the blue-button.py repository:
```shell
git clone https://github.com/LinuxForHealth/connect-clients.git
```

## Start the Blue Button client
Start the Blue Button client from the command line from the LinuxForHealth connect-clients repo:
```shell
cd connect-clients/blue-button.py
pip install --upgrade pip
pipenv sync --dev
pipenv run bluebutton
```

## Test the Blue Button client

### Invoke the /bluebutton/authorize endpoint
- Open your browser and navigate to the Blue Button client OpenAPI doc at https://127.0.0.1:5200/docs
- Click on the GET /bluebutton/authorize endpoint.
- Click 'Try it out' and then click 'Execute'.
  
### Authorize the LinuxForHealth application
- Log in using [synthetic login credentials](https://bluebutton.cms.gov/developers/), e.g. user: BBUser02001 and password: PW02001!
- Select 'Share all of your data', which will allow you to retrieve Patient, ExplanationOfBenefit and Coverage FHIR synthetic resources to send to LinuxForHealth.
- Click 'Allow'.  You should see a result similar to:
```shell
{
  "access_token":"8VTaFWphdFZWXAg1kJr2vR2bW4vqfE",
  "expires_in":36000,
  "token_type":"Bearer",
  "scope":"introspection patient/Coverage.read patient/ExplanationOfBenefit.read patient/Patient.read profile",
  "refresh_token":"h5rSLuKCC2cVdOGKLE8JPJGv8UPSUa",
  "patient":"-19990000002002"
}
```
- Copy the value of "access_token" and keep the tab open, as you will need the value for "patient" in a later step.
  
### Set the authorization token
- Switch tabs back to the Blue Button client OpenAPI doc at https://127.0.0.1:5200/docs
- Click the Authorize button.
- Paste the copied access token and click 'Authorize' then click 'Close'.

### Retrieve Blue Button FHIR data and send it to LinuxForHealth connect
- Click on the GET /bluebutton/fhir endpoint and click 'Try it out'.
- Fill out the 3 fields as follows:

    - resource_type: Patient   (Possible types: Patient, Coverage, ExplanationOfBenefit)
    - patient: Paste the value of the "patient" field from the Blue Button login result
    - return_cms: Select True to view the bundle returned from CMS.
    
- Click 'Execute'.  You should see a Bundle containing a Patient resource, similar to:

```text
{
  "resourceType": "Bundle",
  "id": "3f56955b-1e33-40f7-91bb-c1cdb29dc23b",
  "meta": {
    "lastUpdated": "2021-09-23T13:36:42.530-04:00"
  },
  "type": "searchset",
  "total": 1,
  "link": [
    {
      "relation": "first",
      "url": "https://sandbox.bluebutton.cms.gov/v2/fhir/Patient?_format=application%2Fjson%2Bfhir&startIndex=0&_count=10&_id=-19990000002002"
    },
    {
      "relation": "last",
      "url": "https://sandbox.bluebutton.cms.gov/v2/fhir/Patient?_format=application%2Fjson%2Bfhir&startIndex=0&_count=10&_id=-19990000002002"
    },
    {
      "relation": "self",
      "url": "https://sandbox.bluebutton.cms.gov/v2/fhir/Patient/?_count=10&_format=application%2Fjson%2Bfhir&_id=-19990000002002&startIndex=0"
    }
  ],
  "entry": [
    {
      "resource": {
        "resourceType": "Patient",
        "id": "-19990000002002",
...
```

### View the LinuxForHealth connect result message
While the result returned from the REST endpoint in the previous step is the FHIR resource returned from the CMS Blue Button 2.0 API, the resource was sent to LinuxForHealth.  You can send the resource to LinuxForHealth again and view the resulting LinuxForHealth message envelope by selecting 'False' for 'return_cms' and clicking 'Execute' again.  You should see a result similar to:

```text
{
  "uuid": "73a98177-c245-4222-a677-5e65e2a63e24",
  "lfh_id": "bbdbcfc4d0f8",
  "operation": "POST",
  "creation_date": "2021-11-02T19:31:01+00:00",
  "store_date": "2021-11-02T19:31:01+00:00",
  "consuming_endpoint_url": "/fhir/Bundle",
  "data": "eyJyZXNvdXJjZVR5cGUiOiAi=",
  "data_format": "FHIR-R4_BUNDLE",
  "status": "success",
  "data_record_location": "FHIR-R4_BUNDLE:0:16",
  "target_endpoint_urls": [],
  "ipfs_uri": "/ipfs/QmTd9usHoLYX6L64Ww6yKjynaWsq1B7JgNYRDs7vySJuv5",
  "elapsed_storage_time": 0.020418,
  "transmit_date": null,
  "elapsed_transmit_time": null,
  "elapsed_total_time": 0.179415,
  "transmission_attributes": "eyJob3N0IjogImx0="
}
```
The 'data_record_location' field indicates the topic:partition:offset of the data stored in the longitudinal patient record via LinuxForHealth.

### Test with other resource types
Vary the resource type and return result type to view other Blue Button data and LinuxForHealth results.
