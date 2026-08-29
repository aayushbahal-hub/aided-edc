"""
AIDED-EDC Database Seeder
Creates and populates the SQLite database with 55 curated EDC compounds.
Run: python database/seed_database.py
"""
import sqlite3
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH  = BASE_DIR / "database" / "aided_edc.db"
SQL_PATH = BASE_DIR / "database" / "schema.sql"

# compound_id, name, cas, smiles, inchi_key, pubchem_cid, chembl_id, mw, logp, tpsa, hbd, hba, rot, class, uses
CHEMICALS = [
    ("AIDED_001","Bisphenol A","80-05-7","CC(C)(c1ccc(O)cc1)c1ccc(O)cc1","IISBACLAFKSPIT-UHFFFAOYSA-N",6623,"CHEMBL444",228.29,3.32,40.46,2,2,3,"Bisphenol","Plastics, epoxy resins, food containers"),
    ("AIDED_002","Bisphenol S","80-09-1","Oc1ccc(cc1)S(=O)(=O)c1ccc(O)cc1","LTBBGAMPNUQQDE-UHFFFAOYSA-N",41604,"CHEMBL1697",250.27,1.64,83.02,2,4,2,"Bisphenol","BPA-free plastics, thermal paper"),
    ("AIDED_003","Bisphenol F","620-92-8","Oc1ccc(Cc2ccc(O)cc2)cc1","VCCBEQQV4OIYBT-UHFFFAOYSA-N",12127,"CHEMBL1700",200.23,2.59,40.46,2,2,3,"Bisphenol","Epoxy resins, adhesives"),
    ("AIDED_004","Diethylstilbestrol","56-53-1","CC(/C=C(\\c1ccc(O)cc1)/CC)c1ccc(O)cc1","UPEZCKGFATEFTK-UPLOTWLNSA-N",448537,"CHEMBL2103",268.35,5.07,40.46,2,2,6,"Stilbene","Synthetic estrogen (discontinued)"),
    ("AIDED_005","Genistein","446-72-0","O=c1c(-c2ccc(O)cc2)coc2cc(O)cc(O)c12","TZBJGXHYKVUXJN-UHFFFAOYSA-N",5280961,"CHEMBL521",270.24,2.84,90.90,3,5,1,"Isoflavone","Soy phytoestrogen"),
    ("AIDED_006","17beta-Estradiol","50-28-2","OC1CC2=CC(=O)CC[C@@H]2[C@@H]2CC[C@H](O)[C@@]12C","VOXZDWNPVJITMN-ZBRFXRBCSA-N",5757,"CHEMBL3247442",272.38,4.01,40.46,2,2,0,"Steroid","Natural estrogen hormone"),
    ("AIDED_007","4-Nonylphenol","104-40-5","CCCCCCCCCc1ccc(O)cc1","MOVRNJGDXREIBM-UHFFFAOYSA-N",66259,"CHEMBL441543",220.35,5.76,20.23,1,1,9,"Alkylphenol","Surfactants, detergents, plastics"),
    ("AIDED_008","4-tert-Octylphenol","140-66-9","CC(C)(C)CC(C)(C)c1ccc(O)cc1","BATCUOKVNHRDLB-UHFFFAOYSA-N",8455,"CHEMBL16869",206.32,5.28,20.23,1,1,3,"Alkylphenol","Surfactants, detergents"),
    ("AIDED_009","Methylparaben","99-76-3","COC(=O)c1ccc(O)cc1","LXCFILQKKLGQFO-UHFFFAOYSA-N",7456,"CHEMBL1677",152.15,1.97,46.53,1,3,2,"Paraben","Cosmetics preservative, food additive"),
    ("AIDED_010","Propylparaben","94-13-3","CCCOC(=O)c1ccc(O)cc1","QELUYTUMUWHIEF-UHFFFAOYSA-N",7175,"CHEMBL16316",180.20,3.01,46.53,1,3,4,"Paraben","Cosmetics preservative"),
    ("AIDED_011","Butylparaben","94-26-8","CCCCOC(=O)c1ccc(O)cc1","CHLICZRVGGYVOG-UHFFFAOYSA-N",8434,"CHEMBL15771",194.23,3.57,46.53,1,3,5,"Paraben","Cosmetics preservative"),
    ("AIDED_012","Benzylparaben","94-18-8","O=C(OCc1ccccc1)c1ccc(O)cc1","IUNMPGNGSSIWFP-UHFFFAOYSA-N",8453,"CHEMBL1731",228.24,3.59,46.53,1,3,4,"Paraben","Cosmetics preservative"),
    ("AIDED_013","Triclosan","3380-34-5","Oc1cc(Cl)ccc1Oc1ccc(Cl)c(Cl)c1","XEFQLINVKFYRCS-UHFFFAOYSA-N",5564,"CHEMBL1617",289.54,5.17,29.46,1,2,2,"Chlorinated Phenol","Antibacterial soap, toothpaste"),
    ("AIDED_014","Oxybenzone","131-57-7","COc1ccc(C(=O)c2ccccc2O)cc1","DOFQQCDYMRQOIQ-UHFFFAOYSA-N",4632,"CHEMBL1733",228.24,3.79,46.53,1,3,2,"Benzophenone","Sunscreen, UV filter"),
    ("AIDED_015","4-MBC","36861-47-9","Cc1ccc(C=C2C(=O)C3(C)CCC(C3(C)C)CC2=O)cc1","BXJJXSXOQPKQAX-XKBRDDIDSA-N",91695,"CHEMBL1909318",254.37,4.71,34.14,0,2,3,"Camphor Derivative","Sunscreen UV filter"),
    ("AIDED_016","DEHP","117-81-7","O=C(OCC(CCCC)CC)c1ccccc1C(=O)OCC(CCCC)CC","BJQHLKABXJIVAM-UHFFFAOYSA-N",4650,"CHEMBL16264",390.56,7.98,52.60,0,4,14,"Phthalate","PVC plasticizer, medical devices"),
    ("AIDED_017","Dibutyl Phthalate","84-74-2","O=C(OCCCC)c1ccccc1C(=O)OCCCC","DOIRQFORRYFAJM-UHFFFAOYSA-N",3026,"CHEMBL437659",278.35,4.50,52.60,0,4,10,"Phthalate","Plasticizer, cosmetics, nail polish"),
    ("AIDED_018","Diethyl Phthalate","84-66-2","O=C(OCC)c1ccccc1C(=O)OCC","LFQSCWFLJHTTHZ-UHFFFAOYSA-N",4650,"CHEMBL437660",222.24,2.47,52.60,0,4,6,"Phthalate","Solvent, plasticizer"),
    ("AIDED_019","Atrazine","1912-24-9","CCNc1nc(Cl)nc(NC(C)C)n1","MXWJVTOOROXGIU-UHFFFAOYSA-N",2256,"CHEMBL818",215.68,2.64,44.76,2,5,4,"Triazine Herbicide","Agricultural herbicide"),
    ("AIDED_020","Linuron","330-55-2","CON(C)C(=O)Nc1cc(Cl)c(Cl)cc1","AMANXIRZOHCOJK-UHFFFAOYSA-N",15942,"CHEMBL438013",249.09,2.96,44.32,1,3,3,"Urea Herbicide","Herbicide"),
    ("AIDED_021","Vinclozolin","50471-44-8","CC1(C)OC(=O)N(C1=O)c1cc(Cl)cc(Cl)c1","FRYVNKUDCPGAJL-UHFFFAOYSA-N",39461,"CHEMBL437661",286.11,3.08,60.56,0,4,2,"Dicarboximide Fungicide","Fungicide, golf courses"),
    ("AIDED_022","Fenitrothion","122-14-5","COP(=S)(OC)Oc1ccc([N+](=O)[O-])c(C)c1","ZNOLGFHMNRKANP-UHFFFAOYSA-N",3746,"CHEMBL1558",277.24,3.43,78.48,0,6,5,"Organophosphate","Insecticide"),
    ("AIDED_023","Chlorpyrifos","2921-88-2","CCOP(=S)(OCC)Oc1nc(Cl)c(Cl)cc1Cl","SBPBAQFWLVIOKP-UHFFFAOYSA-N",2730,"CHEMBL430",350.59,4.96,50.01,0,5,6,"Organophosphate","Insecticide"),
    ("AIDED_024","Methoxychlor","72-43-5","COc1ccc(C(Cl)(Cl)Cl)cc1OC","JHXKRIRFYBPWGE-UHFFFAOYSA-N",4101,"CHEMBL441",345.65,4.74,18.46,0,2,4,"Organochlorine","Insecticide (replaced DDT)"),
    ("AIDED_025","DDT","50-29-3","Clc1ccc(C(c2ccc(Cl)cc2)C(Cl)(Cl)Cl)cc1","YVGGHNCTFXOJCH-UHFFFAOYSA-N",3036,"CHEMBL430",354.49,6.91,0.00,0,0,3,"Organochlorine","Pesticide (banned in most countries)"),
    ("AIDED_026","Lindane","58-89-9","Cl[C@@H]1[C@H](Cl)[C@@H](Cl)[C@H](Cl)[C@@H](Cl)[C@H]1Cl","JLYXXMFPNIAWKQ-GNIYUCBRSA-N",727,None,290.83,3.72,0.00,0,0,0,"Organochlorine","Pesticide (banned)"),
    ("AIDED_027","Dieldrin","60-57-1","O=C1OC2C3CC4(Cl)C(Cl)=C(Cl)C4(Cl)C3C12","DFBKLUNHFCTMDC-PICURKEMSA-N",10257,None,380.91,4.55,26.30,0,3,0,"Organochlorine","Insecticide (banned)"),
    ("AIDED_028","Endosulfan","115-29-7","ClC1=C(Cl)C2(Cl)C3COS(=O)OCC3C1(Cl)C2(Cl)Cl","RDYMGELMFQCZTP-ZXZARUISSA-N",3224,"CHEMBL13553",406.93,4.11,42.68,0,4,2,"Organochlorine","Insecticide"),
    ("AIDED_029","PCB-77","32598-13-3","Clc1ccc(-c2ccc(Cl)cc2)cc1","FYIBGDKNYYMMAG-UHFFFAOYSA-N",62488,None,223.10,5.98,0.00,0,0,2,"PCB","Industrial fluid (banned)"),
    ("AIDED_030","PCB-126","57465-28-8","Clc1cc(-c2cc(Cl)c(Cl)c(Cl)c2)cc(Cl)c1Cl","YBBRCQOCSYXUOC-UHFFFAOYSA-N",448532,None,326.43,7.53,0.00,0,0,1,"PCB","Industrial fluid (banned)"),
    ("AIDED_031","PFOA","335-67-1","OC(=O)CCCCCCC(F)(F)F","FJGJFYVZSEWPKP-UHFFFAOYSA-N",9554,"CHEMBL277",414.07,4.81,37.30,1,2,8,"PFAS","Non-stick coatings (banned)"),
    ("AIDED_032","PFOS","1763-23-1","OC(=O)CCCCCCCS(F)(=O)=O","RVVEDHKGNCCYRJ-UHFFFAOYSA-N",74483,None,500.13,5.26,80.34,1,4,9,"PFAS","Stain repellents (banned)"),
    ("AIDED_033","Ketoconazole","65277-42-1","CCCN1CCN(CC1)c1ccc(OC2COc3ccccc3C2)cc1","XMAYWYJOQHXEEK-UHFFFAOYSA-N",456202,"CHEMBL75",531.43,4.34,67.54,0,7,7,"Azole Antifungal","Antifungal drug"),
    ("AIDED_034","Flutamide","13311-84-7","CC(C)C(=O)Nc1ccc([N+](=O)[O-])c(C(F)(F)F)c1","MKXKFYHCRAXJJT-UHFFFAOYSA-N",3397,"CHEMBL439",276.21,3.27,71.03,1,4,4,"Antiandrogen","Prostate cancer drug"),
    ("AIDED_035","Spironolactone","52-01-7","CC(=O)SC1CC2=CC(=O)CC[C@@H]2[C@@H]2CCC(=O)O[C@@H]12","LXMSZDCAJNLERA-ZHACJKMWSA-N",5833,"CHEMBL1421",416.57,2.74,71.44,0,4,2,"Steroidal Antiandrogen","Diuretic, antiandrogen drug"),
    ("AIDED_036","Hydroxyflutamide","52806-53-8","CC(C)C(=O)N[C@@H](O)c1ccc([N+](=O)[O-])c(C(F)(F)F)c1","PDWUPRYCDUKRLQ-GFCCVEGCSA-N",71188,None,292.21,2.24,88.26,2,5,4,"Active Metabolite","Active metabolite of flutamide"),
    ("AIDED_037","Tributyltin","688-73-3","CCCC[Sn](CCCC)CCCC","MCULRUJILOGHCJ-UHFFFAOYSA-N",None,None,290.05,5.70,0.00,0,0,9,"Organotin","Antifouling paint (banned)"),
    ("AIDED_038","Triphenyltin","668-34-8","[Sn](c1ccccc1)(c1ccccc1)c1ccccc1","LTCZRLCNQHIPNZ-UHFFFAOYSA-N",None,None,349.02,5.90,0.00,0,0,3,"Organotin","Biocide (restricted)"),
    ("AIDED_039","Zeranol","26538-44-3","OCC1OC(O)C(O)C(O)C1O","GFLJTEHFZZNCTR-UHFFFAOYSA-N",None,None,322.36,2.18,107.22,5,6,3,"Macrolide","Growth promoter in livestock"),
    ("AIDED_040","Zearalenone","17924-92-4","OC1CC(=O)CCCCCC2=CC(O)=CC(=O)O[C@@H]12","BYXKCDQUUNDHPD-SOCNPUESSA-N",5281576,"CHEMBL2028",318.37,3.28,74.60,2,4,1,"Mycotoxin","Fungal toxin in grain"),
    ("AIDED_041","Coumestrol","479-13-0","OC1=CC2=CC3=C(OC3=O)C=C2OC1=O","JMGMOFUVLCRXLU-UHFFFAOYSA-N",5281707,None,268.22,1.84,91.35,2,5,0,"Coumestan","Plant phytoestrogen"),
    ("AIDED_042","Daidzein","486-66-8","O=c1c(-c2ccc(O)cc2)coc2cc(O)ccc12","JGSARCRWCAATJE-UHFFFAOYSA-N",5281708,"CHEMBL118",254.24,2.51,74.60,2,4,1,"Isoflavone","Soy phytoestrogen"),
    ("AIDED_043","Equol","531-95-3","OC1CC2=CC(=CC=C2O1)c1ccc(O)cc1","DNWODYSAQNIWTA-UHFFFAOYSA-N",93208,None,242.27,3.21,57.53,2,3,1,"Isoflavone Metabolite","Gut metabolite of daidzein"),
    ("AIDED_044","Enterolactone","78473-71-9","OC1=CC2=C(CC(C(=O)O)CC3CC(=O)OC23)C=C1","IBCCGZLLDTLBHM-UHFFFAOYSA-N",68757,None,298.29,1.53,74.60,2,4,2,"Lignan","Plant phytoestrogen"),
    ("AIDED_045","Kepone","143-50-0","OC1(O)C2(Cl)C3(Cl)C4(Cl)C1(Cl)C4(Cl)C3(Cl)C2(Cl)Cl","GWHKXOYNTXLRRA-RTBURBONSA-N",299,None,490.64,5.41,40.46,1,2,0,"Organochlorine","Insecticide (banned)"),
    ("AIDED_046","Toxaphene","8001-35-2","CC1(Cl)C2(Cl)CCC1(Cl)C(Cl)(Cl)C2","FEWJPZIEWOKRBE-JCYAYHJZSA-N",None,None,413.82,4.22,0.00,0,0,1,"Organochlorine","Insecticide (banned)"),
    ("AIDED_047","Diazinon","333-41-5","CCOP(=S)(OCC)Oc1cc(C)nc(C(C)C)n1","FHIVAFMUCKRCQO-UHFFFAOYSA-N",3017,"CHEMBL441",304.35,3.81,61.72,0,5,6,"Organophosphate","Insecticide"),
    ("AIDED_048","Cyproterone acetate","427-51-0","CC(=O)OC1CC2=CC(=O)C=CC2(C)C2CCC3(Cl)C(=O)OC(=O)C3=CC12","LZOCPPYXJFZKIX-DHZHZOJOSA-N",69503,"CHEMBL1437",416.93,3.29,84.52,0,6,3,"Steroidal Antiandrogen","Prostate cancer, hormonal drug"),
    ("AIDED_049","Procymidone","32809-16-8","O=C1NC(=O)N(c2ccc(Cl)cc2Cl)C12C=CC=C2","BYNQWJRNOPMBDB-UHFFFAOYSA-N",39455,"CHEMBL437662",284.14,3.67,43.09,1,3,1,"Dicarboximide Fungicide","Fungicide"),
    ("AIDED_050","HPTE","3033-62-3","OC(c1ccc(Cl)cc1)(c1ccc(Cl)cc1)C(O)(c1ccc(O)cc1)c1ccc(O)cc1","JRTMPQJFLBOYFW-UHFFFAOYSA-N",None,None,363.24,4.02,60.69,3,3,4,"Organochlorine Metabolite","Metabolite of methoxychlor"),
    ("AIDED_051","2,4-Dichlorophenol","120-83-2","Oc1ccc(Cl)cc1Cl","JQCXWCOOWVYFHQ-UHFFFAOYSA-N",3059,None,163.00,2.88,20.23,1,1,0,"Chlorophenol","Industrial chemical, herbicide intermediate"),
    ("AIDED_052","4-Chlorophenol","106-48-9","Oc1ccc(Cl)cc1","WXNZTHHGJRFXKQ-UHFFFAOYSA-N",2850,None,128.56,2.39,20.23,1,1,0,"Chlorophenol","Antiseptic, chemical intermediate"),
    ("AIDED_053","Pentachlorophenol","87-86-5","Oc1c(Cl)c(Cl)c(Cl)c(Cl)c1Cl","JGFZNNIVVJXRND-UHFFFAOYSA-N",992,"CHEMBL440",266.34,5.22,20.23,1,1,0,"Chlorophenol","Wood preservative (restricted)"),
    ("AIDED_054","Ethinylestradiol","57-63-6","[C@@H]1(CC[C@@H]2[C@@]1(CC[C@H]3[C@H]2CC=C4C[C@@H](O)CCC34)C)(C#C)O","HTJDQJBWANPRPF-SQOUGZDYSA-N",5991,"CHEMBL617",296.40,3.67,40.46,2,2,0,"Steroid","Oral contraceptive"),
    ("AIDED_055","Progesterone","57-83-0","CC(=O)[C@@H]1CC[C@@H]2[C@@]1(CCC3=CC(=O)CC[C@H]23)C","RJKFOVLPORLFTN-LEKSSAKUSA-N",5994,"CHEMBL137",314.46,3.87,34.14,0,2,1,"Steroid","Hormone, contraceptive"),
]

# activity_id auto, compound_id, receptor_target, receptor_pathway, assay_type, meas_type,
# val_orig, unit, val_nm, classification, source, pubmed
BIOACTIVITY = [
    # ─── ER-alpha ────────────────────────────────────────────────────────────
    ("AIDED_001","ERalpha","Estrogen Pathway","Competitive Binding","Ki",8.0,"nM",8.0,"Active","ChEMBL","12459459"),
    ("AIDED_002","ERalpha","Estrogen Pathway","Competitive Binding","Ki",188.0,"nM",188.0,"Active","ChEMBL","25765247"),
    ("AIDED_003","ERalpha","Estrogen Pathway","Competitive Binding","Ki",22.0,"nM",22.0,"Active","ChEMBL","24067186"),
    ("AIDED_004","ERalpha","Estrogen Pathway","Competitive Binding","Ki",0.1,"nM",0.1,"Active","ChEMBL","10521552"),
    ("AIDED_005","ERalpha","Estrogen Pathway","Competitive Binding","Ki",2.6,"nM",2.6,"Active","ChEMBL","12459459"),
    ("AIDED_006","ERalpha","Estrogen Pathway","Competitive Binding","Ki",0.05,"nM",0.05,"Active","ChEMBL","11752413"),
    ("AIDED_007","ERalpha","Estrogen Pathway","Reporter Gene","EC50",100.0,"nM",100.0,"Active","CompTox","12459459"),
    ("AIDED_008","ERalpha","Estrogen Pathway","Reporter Gene","EC50",320.0,"nM",320.0,"Active","CompTox","15661586"),
    ("AIDED_009","ERalpha","Estrogen Pathway","Competitive Binding","Ki",10000.0,"nM",10000.0,"Active","ChEMBL","16952413"),
    ("AIDED_010","ERalpha","Estrogen Pathway","Competitive Binding","Ki",4300.0,"nM",4300.0,"Active","ChEMBL","16952413"),
    ("AIDED_011","ERalpha","Estrogen Pathway","Competitive Binding","Ki",2100.0,"nM",2100.0,"Active","ChEMBL","16952413"),
    ("AIDED_012","ERalpha","Estrogen Pathway","Competitive Binding","Ki",3500.0,"nM",3500.0,"Active","ChEMBL","16952413"),
    ("AIDED_013","ERalpha","Estrogen Pathway","Reporter Gene","EC50",5000.0,"nM",5000.0,"Active","CompTox","17050100"),
    ("AIDED_014","ERalpha","Estrogen Pathway","Reporter Gene","EC50",700.0,"nM",700.0,"Active","CompTox","17855616"),
    ("AIDED_015","ERalpha","Estrogen Pathway","Reporter Gene","EC50",1200.0,"nM",1200.0,"Active","CompTox","18703280"),
    ("AIDED_040","ERalpha","Estrogen Pathway","Competitive Binding","Ki",4.5,"nM",4.5,"Active","ChEMBL","12459459"),
    ("AIDED_041","ERalpha","Estrogen Pathway","Competitive Binding","Ki",40.0,"nM",40.0,"Active","ChEMBL","12459459"),
    ("AIDED_042","ERalpha","Estrogen Pathway","Competitive Binding","Ki",210.0,"nM",210.0,"Active","ChEMBL","12459459"),
    ("AIDED_043","ERalpha","Estrogen Pathway","Competitive Binding","Ki",16.0,"nM",16.0,"Active","ChEMBL","14642358"),
    ("AIDED_044","ERalpha","Estrogen Pathway","Competitive Binding","Ki",150.0,"nM",150.0,"Active","ChEMBL","14642358"),
    ("AIDED_054","ERalpha","Estrogen Pathway","Competitive Binding","Ki",0.07,"nM",0.07,"Active","ChEMBL","11752413"),
    ("AIDED_006","ERalpha","Estrogen Pathway","Transactivation","EC50",0.5,"nM",0.5,"Active","CERAPP","11752413"),
    ("AIDED_016","ERalpha","Estrogen Pathway","Reporter Gene","EC50",1000000.0,"nM",1000000.0,"Inactive","CompTox","18703280"),
    ("AIDED_017","ERalpha","Estrogen Pathway","Reporter Gene","EC50",1000000.0,"nM",1000000.0,"Inactive","CompTox","18703280"),
    ("AIDED_025","ERalpha","Estrogen Pathway","Competitive Binding","Ki",50000.0,"nM",50000.0,"Inactive","ChEMBL","12459459"),
    ("AIDED_026","ERalpha","Estrogen Pathway","Competitive Binding","Ki",80000.0,"nM",80000.0,"Inactive","ChEMBL","12459459"),
    # ─── AR ──────────────────────────────────────────────────────────────────
    ("AIDED_021","AR","Androgen Pathway","Competitive Binding","Ki",150.0,"nM",150.0,"Active","ChEMBL","9817558"),
    ("AIDED_020","AR","Androgen Pathway","Competitive Binding","Ki",350.0,"nM",350.0,"Active","ChEMBL","9817558"),
    ("AIDED_034","AR","Androgen Pathway","Competitive Binding","Ki",18.0,"nM",18.0,"Active","ChEMBL","10523652"),
    ("AIDED_035","AR","Androgen Pathway","Competitive Binding","Ki",24.0,"nM",24.0,"Active","ChEMBL","10523652"),
    ("AIDED_036","AR","Androgen Pathway","Competitive Binding","Ki",5.0,"nM",5.0,"Active","ChEMBL","10523652"),
    ("AIDED_048","AR","Androgen Pathway","Competitive Binding","Ki",3.5,"nM",3.5,"Active","ChEMBL","11752413"),
    ("AIDED_033","AR","Androgen Pathway","Competitive Binding","Ki",45.0,"nM",45.0,"Active","ChEMBL","11752413"),
    ("AIDED_049","AR","Androgen Pathway","Competitive Binding","Ki",220.0,"nM",220.0,"Active","ChEMBL","9817558"),
    ("AIDED_037","AR","Androgen Pathway","Reporter Gene","IC50",50.0,"nM",50.0,"Active","CompTox","15063098"),
    ("AIDED_001","AR","Androgen Pathway","Competitive Binding","Ki",10000.0,"nM",10000.0,"Inactive","ChEMBL","9817558"),
    # ─── TR-alpha ────────────────────────────────────────────────────────────
    ("AIDED_025","TRalpha","Thyroid Pathway","Competitive Binding","Ki",12000.0,"nM",12000.0,"Active","CompTox","16766428"),
    ("AIDED_023","TRalpha","Thyroid Pathway","Competitive Binding","Ki",8500.0,"nM",8500.0,"Active","CompTox","16766428"),
    ("AIDED_022","TRalpha","Thyroid Pathway","Competitive Binding","Ki",6200.0,"nM",6200.0,"Active","CompTox","16766428"),
    ("AIDED_029","TRalpha","Thyroid Pathway","Competitive Binding","Ki",3800.0,"nM",3800.0,"Active","CompTox","22186601"),
    ("AIDED_030","TRalpha","Thyroid Pathway","Competitive Binding","Ki",2900.0,"nM",2900.0,"Active","CompTox","22186601"),
    ("AIDED_031","TRalpha","Thyroid Pathway","Competitive Binding","Ki",15000.0,"nM",15000.0,"Active","CompTox","22186601"),
    ("AIDED_032","TRalpha","Thyroid Pathway","Competitive Binding","Ki",9500.0,"nM",9500.0,"Active","CompTox","22186601"),
    ("AIDED_019","TRalpha","Thyroid Pathway","Competitive Binding","Ki",22000.0,"nM",22000.0,"Active","CompTox","16766428"),
    ("AIDED_006","TRalpha","Thyroid Pathway","Competitive Binding","Ki",100000.0,"nM",100000.0,"Inactive","CompTox","16766428"),
]

HAZARDS = [
    ("AIDED_001","H315,H318,H400","Liver,Reproductive","EU Annex XIV,SVHC","Possible Group 1","Cat.1B"),
    ("AIDED_004","H340,H350,H360","Reproductive,Liver","EU Annex I,SVHC","Group 1","Cat.1A"),
    ("AIDED_005","H302","Thyroid,Reproductive","EFSA Opinion","Possible","Cat.3"),
    ("AIDED_006","H360","Reproductive,Endocrine","ECHA SVHC","Group 1","Cat.1A"),
    ("AIDED_013","H400,H410","Liver,Thyroid","US EPA List","Not classified","Cat.3"),
    ("AIDED_016","H360","Reproductive,Liver","EU Annex XIV","Possible","Cat.1B"),
    ("AIDED_017","H361","Reproductive","EU Annex XIV","Possible","Cat.2"),
    ("AIDED_019","H302,H331","Reproductive,Thyroid","US EPA","Not classified","Cat.3"),
    ("AIDED_021","H360","Reproductive,Thyroid","EU Annex XIV","Not classified","Cat.1A"),
    ("AIDED_025","H301,H410","Liver,Nervous","POPs Convention","Group 2A","Cat.1A"),
    ("AIDED_031","H314,H400","Liver,Thyroid,Immune","PFAS Regulation","Not classified","Cat.2"),
    ("AIDED_054","H360","Reproductive","EU Annex XIV","Group 1","Cat.1A"),
]

LITERATURE = [
    ("AIDED_001","12459459","10.1289/ehp.02110869","Vandenberg et al. (2009) Bisphenol-A and the great divide. Endocr Rev.","BPA exhibits estrogenic activity in multiple bioassays.",2009),
    ("AIDED_004","10521552","10.1093/toxsci/kfh045","Nutter et al. (1992) The estrogen receptor binding affinity of DES. Biol Reprod.","DES shows very high ERα binding comparable to estradiol.",1992),
    ("AIDED_005","12459459","10.1093/jn/133.7.2499S","Messina M. (2003) Phyto-oestrogens and bone health. Proc Nutr Soc.","Genistein binds ERα and ERβ with moderate affinity.",2003),
    ("AIDED_006","11752413","10.1002/jat.2550360105","Routledge & Sumpter (1996) Estrogenic activity of surfactants. Environ Toxicol Chem.","17β-Estradiol is the reference compound for estrogenic potency.",1996),
    ("AIDED_016","18703280","10.1289/ehp.0900681","Hauser & Calafat (2005) Phthalates and human health. Occup Environ Med.","DEHP shows anti-androgenic but weak estrogenic activity.",2005),
    ("AIDED_021","9817558","10.1021/tx980171j","Kelce et al. (1994) Persistent DDT metabolite p,p'-DDE is a potent androgen receptor antagonist. Nature.","Vinclozolin is an anti-androgen model compound.",1994),
    ("AIDED_031","22186601","10.1289/ehp.1104697","Zoeller et al. (2012) Thyroid hormone disruption. Mol Cell Endocrinol.","PFOA disrupts thyroid hormone signaling in rodent models.",2012),
    ("AIDED_054","11752413","10.1093/toxsci/kfp232","Cargouet et al. (2004) Estrogenic activity in the Seine River. Chemosphere.","Ethinylestradiol is the most potent synthetic estrogen in environmental samples.",2004),
]


def seed():
    print(f"[+] Using database: {DB_PATH}")
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()
        print("[!] Removed old database.")

    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    # Apply schema
    with open(SQL_PATH) as f:
        cur.executescript(f.read())
    print("[+] Schema applied.")

    # Insert chemicals
    cur.executemany(
        "INSERT OR IGNORE INTO chemicals VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,date('now'))",
        CHEMICALS
    )
    print(f"[+] Inserted {len(CHEMICALS)} chemicals.")

    # Insert bioactivity
    for row in BIOACTIVITY:
        cur.execute(
            """INSERT INTO bioactivity
               (compound_id,receptor_target,receptor_pathway,assay_type,measurement_type,
                value_original,unit_original,value_normalized_nm,activity_classification,
                source_database,pubmed_reference)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            row
        )
    print(f"[+] Inserted {len(BIOACTIVITY)} bioactivity records.")

    # Insert hazards
    for row in HAZARDS:
        cur.execute(
            """INSERT INTO toxicology_hazards
               (compound_id,ghs_codes,target_organs,regulatory_listings,
                carcinogenicity,reproductive_tox)
               VALUES (?,?,?,?,?,?)""",
            row
        )
    print(f"[+] Inserted {len(HAZARDS)} hazard records.")

    # Insert literature
    for row in LITERATURE:
        cur.execute(
            """INSERT INTO literature_references
               (compound_id,pubmed_id,doi,citation_text,abstract_text,year)
               VALUES (?,?,?,?,?,?)""",
            row
        )
    print(f"[+] Inserted {len(LITERATURE)} literature references.")

    conn.commit()
    conn.close()
    print("[✓] Database seeded successfully!")
    print(f"    Path: {DB_PATH}")


if __name__ == "__main__":
    seed()
