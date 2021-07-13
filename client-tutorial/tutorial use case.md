# Tutorial Use Case for Linux For Health: Legacy clinical system to FHIR enabled
### Henry Feldman MD, FACP, FHM, FAMIA
### CMO for Development

## Background
this document is a tutorial (more of a guide) about using LFH in the use case of an existing clinical database for a legacy piece of software.
While this document may not be exactly what your use case if you are dealing with legacy clinical data this hopefully will be a good primer. There will
be some reasonable code examples (mostly in Python, but you can in theory use other languages such as Java, C# ,etc since you comminicate via HTTP posting to the connect tooling)

# Setup
I don't mean how to setup LFH, but more in how your setup likely is. You have some form of clinical database, which is representing some patient or institutional data, either care or claims data,
that you wish to exchange with another system, but your old legacy software can't communicate with as it predates modern protocols such as FHIR. We will now think about the basic workflow on how to go from 
this legacy database to a newer protocol to transmit health data elsewhere in.

The basic workflow is simple enough in concept, but harder in implementation without a framework such as LFH to handle all the important bits for you. So issues you have to worry about in situations
like this is valid formatting of the converted data, reliable delivery of the converted data to the fhri server along with possible ETL enrichment along the way. And doing all that in an auditable way at scale.

For accomplishing this workflow LFH is going to put several useful services up in your environment. The central controller, and what you primarily will interface with is the LFH Connect service.
This is service can be thought of as your central hub. Its primary role is to take in your data, validate it, potentially enrich it through triggered pathways and ultimately post your data to its ultimate destination.
The delivery of your data will take place via 2 services: NATS and Kafka. let's explore what the job of these two services do for your data:

NATS: Nats (https://nats.io/) is a high-speed distributed messaging architecture designed for garaunteed delivery of messages across a network at scale. This service can link a disparate number of data sources such as iOT devices, servers
web services. This makes sure you don't need to worry about *how* your data gets delivered, allowing you to worry about the *what* gets delivered. After NATS delivered the data we need to queue the messages in a way that 
the receivers can consume data at their lesiure. You will note that I said receivers in the plural, which is because often there are multiple entities that want to be informed of a clinical event. NATS is reponsible for securer reliable delivery to subscribed clients

# Time-unwrapping the data
Probably the most important relationship in clinical care is the temporal relationship, and while clinicains often joke that clinical medicine
seems to defy both relativity and quantum mechaninics, cause does really proceed effects. A perfect example that comes up frequently is when we are
looking at a patients with heart failure, knowing the cause of the heart failure can help us select optimal treatments.So we need to put the clinical
events and treatments in a time ordered series; but normally they are stored by category in a database (either relational or heierarchical) which makes
exploring these relationships technically tricky to do. Now most of the time you wouldn't want to see clinical data laid out in this manner, But answering the
question of what is the history of this condition. In sticking with our above example let's imagine the classic *ischemic cardiomyopathy* as the cause of 
the patient's heart failure. So first we want to look at the patient's first event (which in that case would be a myocardial infarction (for this example we will assume a STEMI))
We see the patient subsequently was brought to the cath-lab and a PCI to the LAD was performed with a drug-eluting stent, and the patient's anti-platelet therapy was initiated. 
About 72 hours the patient developed Dressler's Syndrome. A thalium viability scan was performed. The patient was noted having intermittant NSVT. The post-discharge
LVEF was 30%, but given the thalium scan revealed significant mycardial stunning, the assumption of LVEF recorver was predicted. Unfortunately despite
maximal medical therapy the patient did not in fact recover their LVEF on a subsequent echocardiogram, so under MADIT II guidelines the patient had an implantable defibrillator placed
for ongoing CHF with depressed EF <= 35%. This is where apache Kafka comes into to play. All those messages sent via NATS ultimately
get delivered to Kafka's topic queue. You can almost view this feature as a twitter stream of clinical events in time-order. So to accomplish our analysis of the above
series of events we would search the Kafka topic to look for cardiac data resources and then we can compile a timeline for related items. Of course Kafka
does not know the physiologic relationships in the data, but presumably your application does. As anyone who has tried to analyze time series clinical data
is aware, there will be a huge number of noisy irrelevant data points intermixed, and it is your application's role to filter these points out based on clinical
logic.

Time ordered data can also be used to de-noise the problem list of patients (where patients can have appendicitis for years because nobody can tell the episode is
complete). You can of course get trajectory information by regressing the time-axis deltas for data points (shallow slope indicate slow progression). Now again understanding the relevance of the
clinical context to do this analysis is critical. And again time ordering can help by looking at this queue in clusters, so for instance if you saw a pro-BMP measurement,
understanding if this was during a presentation where heart-failure was the primary concern (the more typical) or during a stroke (normally sky-high but not cardiac origin) can be useful for driving
clinical support.. One useful tip for making this kind of analysis possible is to use NLP (such as the Annotator for Clinical Data) to extract information from clinical notes adjascent to the event you 
are examining to get clinical context for a given data point. You can also drive clinical contex fetching using this technique as well.
So let's take another hypothetical case where a patient is presenting with a very altered mental status, and there is concern for stroke vs. a seizure (a common stroke-mimic). As the patient is unable
to present their own history we typically perform a "chart biopsy" to reconstruct their history. This is where using NLP to derive the topics that
the clinician is concentrating on, we can pull related conditions and their history from this time series. So finding a prior EEG in this case
would be useful to know that despite proper anti-epileptic agents (AEDs) the patient continued to demonstrate epileptiform activity
would increase the pre-test probability of seizure as the etiology. The advantage of searching a time series versus a traditional categorized database
is that it searches all data types (so you are simultaneously looking in notes, reports, labs, etc without worrying about the type of data resource). Of course this is less 
efficient when trending a specific data type (if you want the average *serum potassium* this is way less efficient than the traditional database search, and of course
you can do enough work to make the queue act like a traditional database, but there is little reason to do so since databases exist)

The final key function is a **FHIR server** which is provided by the IBM Fhir Server (https://www.ibm.com/products/fhir-server) a full coverage FHIR R4 server. Note a FHIR server (as opposed to just FHIR as a protocol) is an implementation of a database that can store/search/retrieve data in the FHIR Resource format and implements the FHIR protocols to perform the data retrieval/searching. LFH provides a way to perform this asynchronously and in a distributed fashion. The FHIR
server acts like (and is to be honest) a traditional database (it has elements of a *relation* and *hierarchical* database manager, using the FHIR protocol instead of SQL). It implements the usual
CRUD functions that a database is expected to implement.

To start you need to clone the connect project from github, (assuming your computer has git installed - if not at github.com there are directions for adding a git client to your OS), in this case we will use the
command-line client. Create a directory to clone this project into. I call mine *gitclones*, but the name is a personal preference, change to that directory. You will need to set up your github client account. There is a tutorial on github.com
on how to setup the command line client for your account (you will need to setup a ssh key). Enter this command to clone the LFH repository:

```
cd <directory_name>
git clone https://github.com/LinuxForHealth/connect 
```

Now how do all these services actually get coordinated and how much works is it for you to launch and maintain them. Here is the good part, you don't do much at all;
These services are *containerized* inside docker containers, so will launch as a coordinated set automatically. Even better these services will self-configure as part of a docker-compose
configuration. This will launch these services into a cluster with a docker provided VPN amongst the containers. This coordination is described in the file `docker-compose.yml` in the root of the of the project.
This process will automatically download the necessary containers to your system as needed.

To launch the server application, navigate to the conect directory. When you list the directory you will see a file named docker-compose.yml (a YAML [pronounced YAMMEL] file - note YAML is whitespace sensitive so be very
cautious editing this file). To startup the system enter the following command:

```
docker-compose up
```

Note on certain operating systems such as MacOS or Windows, docker runs as a desktop application. You will need to install the docker engine application and run it (like any other regular application) prior to launching LFH for the first time; after the first
time you can start/stop the services within the GUI. To download this engine download at https://www.docker.com/products/docker-desktop

You will see the services start to spin up, and the containers will download. eventually you should see that the docker containers are up and running. Once these services are up and running it is time to get to your side of the application.
Most of the configuration your client code needs can be found in config.py. There are many parameters you can adjust here, bu the most important one that will potentially cause problems later is the rate limiter, which protects against run-away 
processes. By default this is set to 5 packets/second. to change this adjust this line:

```limiter
connect_rate_limit: str = "5/second"
```
You can change 5 to a larger number such as 1000 or something.

# accessing your data
Your data is presumably in some sort of database manager. Depending on how this legacy system was constructed it could use a propietary database, but assuming it is using a regular database manager,
it is likely that python has the capability to connect to that database. In the tutorial here we will use SQLAlchemy (https://www.sqlalchemy.org) which is an ORM (or Object Relation Manager). So what does that
do for you, and why is it a good thing? Well if you've ever connected code with a database (such as MySQL or Postgresql) you likely ran into the situation where the database queries in your code and the
structure of the database became out of synch (such you add a field, and your code is extracting fields by numerical index) In addition SQL queries in your code are not able to be checked by the compiler
for type safety (for instance you specify a text value for a numeric field). So the ORM was invented to remove the whole notion of a database
from your code. Programs oftne have arrays of data objects they manage and ORMs make the database appears as one of those. So you can worry about the *what* not the *how* of your data storage. Most importantly in
clinical applications the ORM can enforce strict type safety for the data, such that floating point values won't get truncated, etc. There are 2 modes you can use to connect SQL Alchemy in (declarative and automatic). In declarative you the programmer
describe the database in a class (in this case we are using the database_classes.py (https://github.ibm.com/henry-feldman/jomis_lfh/blob/master/database_classes.py) file to perform this function) to the ORM. So this python file declares a class for every database table and then describes the columns in that table as a field of
our class. You will note that each data field includes a Column mapping and some internal database description such can the column be set to *null*).

```patientClass
...
class Patient(Base):
    """
     this is the class that is mapped to the PATIENTS table in the database. This table was derived from MIMIC III
     where the data is based on real-world dataset from BIDMC's ICU system (metavision) but then we added a lot of synthetic fields
     """
    __tablename__ = 'PATIENTS'

    ROW_ID = Column(mysql.MEDIUMINT, primary_key=True)
    SUBJECT_ID = Column(mysql.MEDIUMINT, nullable=False, unique=True)
    first_name = Column(String(128), nullable=False, index=True)
    last_name = Column(String(128), nullable=False, index=True)
    street = Column(String(256), nullable=False)
    city = Column(String(256), nullable=False)
    state = Column(String(2), nullable=False, index=True)
    zip = Column(String(10), nullable=False, index=True)
    latitude = Column(DECIMAL(22, 11))
    longitude = Column(DECIMAL(22, 11))
    GENDER = Column(String(5), nullable=False)
    race = Column(String(32), nullable=False, index=True)
    ...
```
Snippet from within database_classes.py where we declare the Patient class (and manually modify for schema changes)

Wait I hear you cry, I have 273 tables in my database with over 1000 fields total. OK, well luckily there are 2 solutions to this, one would be 
to statically generate the mapping file (as I did above) or use automatic mapping (next section). TO do a static generation we use the sqlcodegen command (https://pypi.org/project/sqlacodegen/). This is a popular tool that you can dowload,
and honestly is my recommended technique as static code is safer in a clinical context. Note that sqlcodegen just prints the pythong to the screen so on linux/Unix we redirect output into a file

so change to the directory you wish to generate the database mapping class in and enter:

`sqlacodegen mysql+oursql://user:password@localhost/dbname > database_classes.py`

Obviously change the terms above to match your situation. You can rerun this (although typically when I added a table or such I ran it to the screen or a seperate file and copy the changes into my existing file by hand)

## Automatic Schema Sync
Now this being python (the "just make it work" model) SqlAlchemy can be told to automatically look at the database schema
and modify the program to adjust for schema changes, this has the obvious advantage of keeping the database and code fully synchronized, but also means someone
can make a logically breaking change to the database without you, the application logic developer, understanding what the implications of a change might be. But your code will run
in the sense that SqlAlchemy will change the object mapping to reflect these changes so if a field changes from float to int this is reflected in python, but your logic may be
assuming the input field is a float (in other langauges such as Java this would typically be a breaking change in the compiler)

You will note in the above example that the table name and class name don't have to match (the table is all-caps for historical reasons) which is also nice with legacy systems which might have weird naming conventions (such as <8 chars) 
and you can use a modern descriptive name. The field order (like in python itself) is irrelevant so if you decided to declare subject_ID before row_id in this example it would work identically.
This declaration of the database structure mapping is then pulled into SqlAlchemy's "Base" which when you intialize the engine (as we do in DatabaseUtil.py - https://github.ibm.com/henry-feldman/jomis_lfh/blob/master/databaseUtil.py)
the database engine will pull this declaration in and remember the mapping. If you are coming from Java, this action is similar to the hibernatecfg.xml functionality in the JPA ORM Hibernate. Once the engine is initialized 
You will pull the session from the engine into any class which wishes to query (retrieve from or write to)  The handy feature of ORMs also removes database specific code, so for instance if in the middle of your project you need to change from let's say 
Oracle to DB2 as your database, that is a configuration and driver change rather than worrying about your code. Any structural changes to the database can be added to the database declaration class

## Actually Querying the Database
Since I come from the Java world I am used to the Hibernate ORM structure, so typically in hibernate you create DAO classes which handle the queries for each data type. So for instanc eyou might have a PatientDao class that has methods for handling the persistance of the Patient class in the database. That style is replicated
in this tutorial. So if you look in each of these dao classes (let's take that PatientDao as an example - https://github.ibm.com/henry-feldman/jomis_lfh/blob/master/PatientsDao.py) you can seewe have a few methods that fetch patient records from the
database. You note there is no SQL code in the query methods which is what allows this to be database independent, since there is no sql code to break. Most importantly in most ORMs the input to a query is sanitized to protect against SQL injection attacks.

![](https://imgs.xkcd.com/comics/exploits_of_a_mom.png)

 *(why we sanitize database inputs - although in this application we have very little user supplied data to sanitize)*

OK, now that we've covered ORMs and how this tutorial accesses data, let's look at the tutorial application in a bit more detail and how it's going to move data around.
So the tutorial begins in EntryPoint.py - https://github.ibm.com/henry-feldman/jomis_lfh/blob/master/EntryPoint.py This class uses Kivy - https://kivy.org/#home to generate a 
local desktop GUI application. If you are coming from Java this is similar to Swing in many ways. Now this application is very simple,
so as to not get lost in the demo. But I didn't want it to be so simple that it didn't create the usual user interaction a real-world application would
have. And most demo/tutorials are simplistic that they are hard to justify (like classes have 2 fields, or what have you and don't match real-world issues). So in this case we have pretty
realistic data classes (while your application may have more data on a patient record, it's rich enough here that the complexity is reflected in the tutorial).
This tutorial will cover retrieving a patient record and some ancillary data, creating a clinical note and transmitting all that via LFH Connect to the FHIR server.

Note the entire code required to retrieve a patient and map all the fields is a single line of code (this is a huge advantage of ORMs):

`return self.session.query(Patient).filter(Patient.SUBJECT_ID==subjectId).one()`

The one() method at the end enforces the uniqueness of this record

## Retriving the patient
In our demo we put up a PatientSearchPanel, which is the world's simplest patient lookup which will search the patients table by medical record name (MRN) so you will note there are 2 UI objects (a Text Input which is preset with the demo patient's MRN **959595**), a button at the bottom to fire the search method. Not to be a Kivy tutorial, but Kivy objects use a callback method binding to sink evets from the UI. 
So in this case we will pull patient *GI Joe 959595*. Even though the demo only has 1 patient in the supplied database, it could have millions and the application would run the same way. Now you may wonder why a patient would not use the MRN as the primary key (which in this 
case is Row_ID) which is often what you see in EMRs because occaisionally you end up with a duplicate patient (an unidentified patient is later identified for instance), and you need to 
potentially merge patient records (and of course if you can merge you need to be able to un-merge), so often these are separated concepts. Again this is not critical for this tutorial
but makes the data more realistic for a tutorial.

In this case when the user presses the searchButton, the patientCallBack method is called and pulls the Patient MRN (called patientSubjectId in this tutorial) from the mrnField TextInput (again to make the tutorial simpler I am using globals to share data between the mothods). So after setting the subject ID into the global we then call the *handleSearchResult* method

```callback
  def patientCallBack(self, event):
        """
        Click Handler for the patient search button from PatientSearchScreen=.SearchButton,, and delegates to handleSearchResult to perform
        the actual selection of the patient
        :param event:
        :type event:
        :return:
        :rtype:
        """
        global patientSubjectId
        global mrnField
        global boxLayout
        print("button pressed ", mrnField.text)
        patientSubjectId = mrnField.text
        boxLayout.clear_widgets()
        self.handleSearchResult()
```
The handleSearchResult method goes on to call the *patientsDao* to actually fetch that patient through the getPatient() `        globalPatient = patientsDao.getPatient(patientSubjectId)
`. So now the patient object is up in the global globalPatient. In the process the *handleSearchResult we go on and put up the retrieved patient's info on screen along with a button to kick off the note writing process.
The "note generation" is started in the *createTccccCallback* method where the UI is cleared and then called onto *handleTccccCreation*. We call the appropriate DAO and get the note class back. And then We move on to creating the FHIR resources 
to send via LFH in the *sendToFhirCallback* method.

## Actually sending FHIR via LFH
All of the above is simply getting to this key feature which is the heart of what LFH does. Now your note that the method calls a feature *asyncio* which is because the tramsission to LFH is an asynchronous process. In
Python the built-in asynchio library facilitates this asynchronous method execution. And is somewhat akin to the Java Runnable interface. To make the tutorial simpler, the FHIR resources are pre-generated and stored as JSON in 
the database (in the fhir_json field). In your application you likley will need to generate the FHIR json via a fhir library if your choice. LFH includes the Pydantic library to valid FHIR resources. So if you look in the code in the FHIR sender methods:

```paient
# send the patient resource
async def send_fhir_to_connect(json, fhirserverurl):
    """
    Sends the json payload to the Fhir Server URL (which must contain the resource type as in https://localhost:5000/fhir/MedicationRequest).
    Note the destination is almost always localhost (where the connect service is running not necessarily the fhir server itself
    :param json: (this is the fhir content)
    :type json: 
    :param fhirserverurl: (the URL as in the above text)
    :type fhirserverurl: 
    :return: 
    :rtype: 
    """
    try:
        async with AsyncClient(verify=False) as client:
            result = await client.post(fhirserverurl, json=json)
            print(f"Header: {result.text}")
    except:
        raise
```
As the comment in the code notes, the fhir server's URL also needs to include the resource type as the sender is not generic and needs to know the resource class
to send it. Near the top of the file you see some static definitions for each resource type's URL:

`fhir_r4_externalserver_notes = 'https://localhost:5000/fhir/DocumentReference` 

as an example so in the send above we post the fhir resource (in this case a note - which is represetnted by a DocumentReference object) One important item to note here is that the URL points to localhost, rather than the destination as that is pointing to the LFH Connect service
not the destination. The ultimate desination is handled by Connect with the handoff to NATS to deliver your payload. The FHIR server returns the URL it posted the data to (if you paste this string into your webbrowser you should get your FHIR back from the FHIR server). You will note the FHIR server 
generates a unique id for the resource (UUID) later you can get back to this exact resource via this UUID (which is essentially the primarry key of this record in the FHIR database).

This is not the only way to access your data, as I mentioned before a FHIR server is a traditional database manager, and has robust search tools and using the search API built into the FHIR protocol, we
can retrieve our data as well.

## Next Steps
Now that we've mastered how to use healthcare clinical data, it is now take a walk on the administrative side into payer data. We start that part via this tutorial page: [administrative data tutorial](administrative_data.md)
