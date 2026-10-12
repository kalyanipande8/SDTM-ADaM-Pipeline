/*****************************************************************
Program:    convert_sdtm_adam.sas
Purpose:    Raw EDC -> SDTM (DM, VS) -> ADaM (ADSL, ADVS) conversion
Status:     Authored SAS program, NOT executed in this environment (no
            SAS license available) -- see src/sdtm_conversion.py and
            src/adam_conversion.py for the executed Python mirror of
            this exact conversion logic, validated in src/validation.py.
******************************************************************/

/* Raw -> SDTM DM */
data sdtm.dm;
    length studyid $10 domain $2 usubjid $20;
    set raw.edc_export(keep=SubjNum DOB_raw GENDER_txt TreatmentArm_raw RandDate_raw) nodupkey;
    by SubjNum;
    studyid = "STUDY-001";
    domain = "DM";
    usubjid = catx("-", studyid, SubjNum);
    brthdtc = DOB_raw;
    sex = ifc(GENDER_txt = "Male", "M", "F");
    arm = TreatmentArm_raw;
    rfstdtc = RandDate_raw;
    keep studyid domain usubjid brthdtc sex arm rfstdtc;
run;

/* Raw -> SDTM VS, with VSDY derived relative to RFSTDTC */
proc sql;
    create table sdtm.vs as
    select
        "STUDY-001" as studyid, "VS" as domain,
        catx("-", "STUDY-001", r.SubjNum) as usubjid,
        r.VisitName as visit, "SYSBP" as vstestcd, "Systolic Blood Pressure" as vstest,
        r.SBP_mmHg as vsorres, "mmHg" as vsorresu,
        r.VisitDate_raw as vsdtc,
        intck("day", input(d.rfstdtc, yymmdd10.), input(r.VisitDate_raw, yymmdd10.)) + 1 as vsdy
    from raw.edc_export r
    inner join sdtm.dm d on catx("-","STUDY-001",r.SubjNum) = d.usubjid;
quit;

/* SDTM -> ADaM ADSL: AGE, TRT01P/N, SAFFL, ITTFL derivations */
data adam.adsl;
    set sdtm.dm;
    age = floor(yrdif(input(brthdtc, yymmdd10.), input(rfstdtc, yymmdd10.), "AGE"));
    ageu = "YEARS";
    trt01p = arm;
    if arm = "Placebo" then trt01pn = 0;
    else if arm = "Drug X 10mg" then trt01pn = 1;
    else if arm = "Drug X 20mg" then trt01pn = 2;
    ittfl = ifc(not missing(rfstdtc), "Y", "N");
run;

proc sql;
    update adam.adsl a
    set saffl = case when exists (select 1 from sdtm.vs v where v.usubjid = a.usubjid)
                      then "Y" else "N" end;
quit;
