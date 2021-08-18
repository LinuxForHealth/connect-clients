# The FHIR generation Tutorial
## By Henry Feldman, MD

## Nosotras finalmente En Fuego
OK we are finally getting to making our own FHIR. So in this code block we are going to pull clinical data entities out of our database
(taking the place of our EMR records) and will generate FHIR resources. We will be working with a specific file called: [Fhir Tutorial](fhirTest.py).

This tutorial is pretty simple in that we will pull in a large number of clinical entities (patient, notes, labs, EKGs, radiology) and convert them
to then generate the corresponding FHIR resource. I chose to do nothing with the converted resource (there is a commented out pretty-print on each
type). This is where you could insert whatever you want to do with your FHIR resource.

**this tutorial requires the prior tutorials to setup database access and LFH**

## So how does this work?
let's step through the tutorial

## set up the database acess
First thing the demo does is set up instances of the Sql Aclhemy DAO classes for each clinical entity:
note to import the database entities you import the classes from [database_classes](database_classes.py). You will need to import each class rather than the entire module.
```
    # Set up all the dabatase access classes
    patientDao = PatientsDao()
    reportsDao = ReportsDao()
    labDao = LabDao()
    adtDao = AdtDao()
```

## set up FHIR tooling
Next we instantiate our own FHIR conversion utility (which is going to use LinuxForHeatlh's Pydantic FHIR library for validation)
```
    # Set up the fhir conversion utility (in FhirUtil.py)
    fhirUtil = FhirConverters()
```
In the Java version of this class I created all these methods as static methods, but python doesn't work the same way, so they are instantiated in the parent class


## Making FHIR for non-Python programmers
So for people coming from a language from other than Python, you may be surprised at how the FhirUtil works with the json template of the FHIR resource just plopped right inline'
of the Python code. Well the python crew was clever in that json syntax happens to match python syntax for several key structures (Lists and Dicts) which allows JSON to be inline  
directly in the python code. Then we replace static values where needed with fields of the SqlAlchemy entities from the database

## Convert the patient
So now we are going to fetch the only patient in our demo database (subject ID: 959595). Feel free to uncomment the pprrint to see the output:
You will note the patient has an extension object encoding their geolocation based on their home address (these were previously pre-calculated and stored in the database)
Note the geolocation is the heart of the city since the address is made up synthetically.
```
#get our patient entity from the database - we only have the one patients
patient = patientDao.getPatient('959595')
print(patientDao.getPatientSummary(patient))
# print the patient info to the screnn
print('sending to fhir converter')
fhirPatient  = fhirUtil.getPatientAsFhir(patient)
#now we have the Patient resource (we're going to ignore it here)
# pprint.pprint(fhirPatient.json(), indent=1, depth=5, width=80)
```

## Convert a Note
One of the primary tasks will be to consume a note (and getting that ready for NLP via ACD - don't worry we have a tutorial for that too) and turn it into a DocumentReference.
For those unfamiliar with DocumentReferences, you encode your text inside a XHTML <div> tag. In addition typically you include a Base64 encoded version of the text, so you'll see that.
Note when you pprint the json that Base64 is a giant block of hexidecimal.

## Convert Labs
Labs are a popular target for FHIR transmission since they are A) complex to encode given the wide range of result types and B) Is a great stress test given the typical quantiy of labs in an EMR.
In the test database this was all derived from (before all the synthetic enhancements) there were 27m labs. We have a small extract of 290 here that belong to patient 959595. These labs are
correlated with the notes and other items (such as the EKGs, etc). Note the dates while consistent between the labs are randomized overall to maintain anonymity, to meet Safe Harbor, since this is real patient data.
The challenge with labs is some labs are numeric in result (either decimal or integer) while others are textual (either something like "POSITIVE" or more confusing "1:312" for a dilution from
a western blot or the like (which is *numeric'ish*). Since python can handle variable types and JSON encodes everything as text this works out OK, but just be advised when reading the value.
If you look in the original lab value in the python class you will see 2 fields for the value, "VALUE" and "VALUENUM" so for labs that can be numeric, they have a VALUENUM while labs that aren't a straight
Decimal valid value are only in VALUE. Note if you are European (or your medical system is derived from a european medical background) you likely will find many of the units confusing as in the US
we use regular metric units rather than SI units. Luckily the database includes a normal/abnormal in the FLAG field where you can at least understand the meaning of the value.

*Important Note:* many non-physicians struggle with the normal/abnormal value; because normal and abnormal are closer to the statistical meaning than clinical. An abnormal value is not the same as as clinically significant. Also
there is normally abnormal and abnormally abnormal. For instance if you meausure progresterone levels in a normal woman they should be low on a regular day, however if she is pregnant it should be markedly elevated. So that value will flag
as abnormal (abnormal != bad, I guess on how much you like kids?) So it is important to understand that these values are determined through population studies where a some huge cohort of 18 year old healthy people had labs drawn and the "normals" are the 1 or 2nd standard deviation
for the values. Another perfect example is toxicology labs that often have a low-normal limit, so for instance if you test a tylenol (paracetamol) level in a patient that hadn't taken any tylenol will be marked as abnormal
if the level was 0 since that is below the low-limit (comically implying that people should have a basal level of tylenol). So interpret the abnormal flag with some clinical context. In addition if a patient has a chronic condition
such as chronic kidney disease, their createnine is always 3 (about 3x "normal") but it's *always* 3, so highlighting every 3 in the record isn't helpful to the clinician, they want to know when that value
markedly deviates from that baseline abnormality. So 3.5 is significantly different from 3 (helpful to also track variability to understand when to utilize that flag).

## Convert Practicionters
In MIMIC they call practicioners "CareGivers" so we are going to convert those to FHIR Practicioner resources. Now one flaw (in my opnion - nobody asked me) is that FHIR is highly normalized, which in a relational datbase makes some sense
with in the early days this was a method to reduce storage space (not a problem anymore of course) but more importantly keeps a *single source of truth*. Now in a RDBMS (particularly when using an ORM like Hibernate or SqlAlchemy) it takes all
the relation handling automagically in the background, but FHIR makes this more complicated. Now why am I ranting about normalizing? Well in the case of Practictioner, for some reason they chose not to include any role information in the Practicioner
resource. Essentially the Practicioner resource contains basic name/ID data, but the PracticionerRole resource provides all the detail. Now in the case of my tooling I chose to get around the normalization, since technically you require multiple fetches (there are ways to force lookups as if it is relational)
is to "cheat" by using the FHIR feature called "contained" which every resource has as a built in feature which is a shared feature where there is a list where you can stuff any resource you want. In this case I choose to stuff the PracticionerRole inside the
Practicioner resource inside Contains. So in other words when you use the `getPracticionerWithRoleAsFhir()` method the return type is a regular Practictioner class, but if you access `Practicioner.contains[0]` you will find a PracticionerRole record, where you can get the hospital they work for
along with their title (physician, etc) and the coding scheme for the role. This magic is accomplished here:
```
           practicioner:Practitioner = self.getCareGiverAsFhir(careGiver)
            if practicioner:
                practicionerRole: PractitionerRole = self.getPracticionerRoleAsFhir(careGiver, hospital)
                practicioner.contained = [practicionerRole]
```

This code first creates a Practicioner FHIR resource and then if that succeded (line 2) it then creates a PractitionerRole resource and insert that role into the contained list.

## Radiology Reports
So Reports are very similar to Notes, in that they are a large block of text typically. In certain types of reports there is a call-out that forms the impression. In radiology reportrs there are often pages of technical findings but they aren't synthesized into a single clinical
thought (that is usable into the clinical sense). So when you look at the [RadiologyReport class](database_classes.py) we see an Impression field. That was extracted previously using ACD's section analyzer with a custom dictionary to extract the impression section of the reports (it has many
names in the data set as it turns out). This is very similar in use to the Assessment and Plan section of a clinical note (honestly it's mostly the only part you care about - surgeons sometimes need the raw info above this
as there are often raw measurements in the text they need for surgical planning. Anyway, FHIR has a place in a DiagnosticReport for an impression for just this reason, and that is preserved. You will note the reports are LOINC encoded for the specific
type of report (radiology vs. EKG). In Java my database entities all obey a "reports" interface which allows overriding of the LOINC coding without having to have explicit methods for each class. Note we had previously stored the Practicioner and now we are going to insert that into this DiagnosticReport with the the Practicioner as a Contained so that will accompany the report.

## EKG reports
So EKG reports are remarkably like radiology reports, except are commenting on an EKG (or ECG depending on whether you like german or english acronyms). Anyway, the key difference is the EKG reports are extremely short and don't really need a seperate impression section since there is no huge text blob of the source data.
The database does not have the waveform data for the EKG itself (you could store them as a documentreference with the Base64 encoded image of the EKG image, but that's not the point of this tutorial. So like radiology reports this will pack the text into the DiagnosticReport. Note we had previously stored the Practicioner and now we are going to insert that into this DiagnosticReport with the the Practicioner as a Contained so that will accompany the report.
