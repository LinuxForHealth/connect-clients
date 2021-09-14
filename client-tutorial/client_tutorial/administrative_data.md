# The administrative data part of the tutorial
## Henry Feldman MD, FACP, FHM, FAMIA
## CMO for Development

### this part of the tutorial is to use the administrative (billing) data in the tutorial database.
In the database we include several tables and classes in python that represent these adminiatrative data elements. The administrative data is arranged slightly hierarchically, similar to the order of the clinical workflow.

the code for this section is in [billing.py](billing.py) which you should run  
All the administrative type data is handled by [ADTDao.py](ADTDao.py). In this case the *Admission* class is the first item to select. You should fetch
the admissions for the patient (the admissions are mapped via the *subject_id* field). The admissions have an id that indexes into the other
data via the HADM_ID (Hospital Admission ID) field.

There are 3 payer tables you can glean for an admission:

DRG codes (for the hospital), CPT codes (for the daily E&M billing) and finally the supporting ICD codes for all of these bills. When you run billing.py you will see a report
which will print to the console (unlike the clinical demo this is in the console). First printed item is the 
admission:
```admit
Admission: EMERGENCY ROOM ADMIT, Date: 12/04/2019 19:49
```

Then we iterate over each DRG:
```DRG
DRG: 1364: APR : Severity/Mortality: 4/4  Respiratory Malignancy
		ICD Codes
		1628 - Malignant neoplasm of other parts of bronchus or lung
		51881 - Acute respiratory failure
		...
```

If you look in the database you note the ICD table is made up of 2 tables (D_DIAGNOSIS_ICD) and (DIAGNOSES_ICD). Since these are
extracts (synthetically enhanced) contain a massive table of ICD codes, many of which are repeated thousands of times, so to reduce storage this is normalized into 2 tables. So the definitions
are in the `D_DIAGNOSIS_ICD` table, while the individual billed ICD codes are in the `DIAGNOSES_ICD` table (keyed to the `HADM_ID`).

`CPTEVENTS` is another split table where the definitional values are in `D_CPT` while the actual billed CPT codes are in `CPTEVENTS`. Like all the others we have 
python classes via SqlAlchemy to retrieve these.

### The Data Dictionaries
The definitional tables are pulled in as python *dictionaries* (so {`id, record}`) Then when you pull the records you can join in program with the defintion. Of course we could
do an in database join in SqlAlchemy, but that is much more computationally intensive and if running the LFH tutorial on a smaller device
such as a Raspberry Pi, then that join will place a much larger load on the system compared to a simple dictionary lookup. In a real clinical scenario you would probably want to do the join
in database given you are likely running a large powerful enterprise server with sufficient RAM too store indexes in RAM.
In ADTDao.py there are several methods that fetch the dictionaries:

* getICDDefinitions()
* getCareGiverDict()
* getCptEventDefinitions()

these fetch the ICD Code definitions, Caregivers (doctors, nurses, etc), CPTCode definitions respectively.
The CPT definitions are less required as much of the information required for billing is located in the CPTEVENTS table and class.

## Modifying `billing.py`
Where would I go from here? Well this is where the 2 roads diverge: you can go the FHIR route and convert these claims data into FHIR resources and send them like we did in the main tutorial or switch 
to X12 (**Warning: Thar be dragons!**)

## Next Tutorial
This is **finally** the link to the FHIR generation we mentioned multiple pages ago. So we need to go to [FhirTutorial.md](FhirTutorial.md)
