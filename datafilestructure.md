# Data File Structures

This document outlines the data structures for the various downloaded data files, based on their CSV headers and API responses.

## CFTC Swap Data (JSON Format)

### Swap Dealers and Major Swap Participants
```json
{
  "legal_name": "string - Legal name of the entity",
  "dftc_swap_dealer_id": "string - Unique identifier for swap dealers",
  "dftc_major_swap_participant_id": "string - Unique identifier for major swap participants",
  "dco_swap_dealer_id": "string - DCO swap dealer identifier",
  "dco_major_swap_participant_id": "string - DCO major swap participant identifier",
  "dcm_swap_dealer_id": "string - DCM swap dealer identifier",
  "dcm_major_swap_participant_id": "string - DCM major swap participant identifier",
  "swap_dealer_status": "string - Registration status as a swap dealer",
  "major_swap_participant_status": "string - Registration status as a major swap participant",
  "registration_status": "string - Overall registration status",
  "registration_date": "date - Date of registration",
  "registration_effective_date": "date - Effective date of registration",
  "registration_withdrawal_date": "date - Date of withdrawal from registration",
  "registration_withdrawal_effective_date": "date - Effective date of withdrawal",
  "registration_withdrawal_reason": "string - Reason for withdrawal",
  "registration_withdrawal_other_reason": "string - Additional withdrawal details",
  "registration_withdrawal_comments": "string - Additional comments on withdrawal"
}
```

### Swap Execution Facilities (SEFs)
```json
{
  "legal_name": "string - Legal name of the SEF",
  "sef_id": "string - Unique identifier for the SEF",
  "sef_registration_status": "string - Registration status of the SEF",
  "sef_registration_date": "date - Date of SEF registration",
  "sef_registration_effective_date": "date - Effective date of SEF registration",
  "sef_website": "string - Official website URL",
  "sef_contact_name": "string - Primary contact person",
  "sef_contact_title": "string - Title of the contact person",
  "sef_contact_phone": "string - Contact phone number",
  "sef_contact_email": "string - Contact email address"
}
```

### Swap Data Repositories (SDRs)
```json
{
  "legal_name": "string - Legal name of the SDR",
  "sdr_id": "string - Unique identifier for the SDR",
  "sdr_registration_status": "string - Registration status of the SDR",
  "sdr_registration_date": "date - Date of SDR registration",
  "sdr_registration_effective_date": "date - Effective date of SDR registration",
  "sdr_website": "string - Official website URL",
  "sdr_contact_name": "string - Primary contact person",
  "sdr_contact_title": "string - Title of the contact person",
  "sdr_contact_phone": "string - Contact phone number",
  "sdr_contact_email": "string - Contact email address"
}
```

### Daily Swap Reports (CSV Format)
```
- report_date: Date - Date of the report
- asset_class: String - Asset class (e.g., Interest Rate, Credit, Equity, Commodity, FX)
- product_type: String - Type of swap product
- product_subtype: String - Subcategory of the swap product
- notional_amount: Decimal - Total notional amount
- trade_count: Integer - Number of trades
- counterparty_type: String - Type of counterparty
- clearing_status: String - Whether the swap is cleared
- execution_type: String - Method of execution (e.g., Voice, Electronic, Hybrid)
- block_trade: Boolean - Whether it's a block trade
- block_trade_eligible: Boolean - Whether the trade is eligible for block trading
- compression_trade: Boolean - Whether it's a compression trade
- package_trade: Boolean - Whether it's part of a package trade
```

## CFTC Data (Equity, Credit, Commodities, Interest Rates)

## CFTC Data (Equity, Credit, Commodities, Interest Rates)

The following data structure is common across all CFTC asset classes (`CFTC_EQ`, `CFTC_CR`, `CFTC_CO`, `CFTC_IR`):

```
- Dissemination Identifier
- Original Dissemination Identifier
- Action type
- Event type
- Event timestamp
- Amendment indicator
- Asset Class
- Product name
- Cleared
- Mandatory clearing indicator
- Execution Timestamp
- Effective Date
- Expiration Date
- Maturity date of the underlier
- Non-standardized term indicator
- Platform identifier
- Prime brokerage transaction indicator
- Block trade election indicator
- Large notional off-facility swap election indicator
- Notional amount-Leg 1
- Notional amount-Leg 2
- Notional currency-Leg 1
- Notional currency-Leg 2
- Notional quantity-Leg 1
- Notional quantity-Leg 2
- Total notional quantity-Leg 1
- Total notional quantity-Leg 2
- Quantity frequency multiplier-Leg 1
- Quantity frequency multiplier-Leg 2
- Quantity unit of measure-Leg 1
- Quantity unit of measure-Leg 2
- Quantity frequency-Leg 1
- Quantity frequency-Leg 2
- Notional amount in effect on associated effective date-Leg 1
- Notional amount in effect on associated effective date-Leg 2
- Effective date of the notional amount-Leg 1
- Effective date of the notional amount-Leg 2
- End date of the notional amount-Leg 1
- End date of the notional amount-Leg 2
- Call amount-Leg 1
- Call amount-Leg 2
- Call currency-Leg 1
- Call currency-Leg 2
- Put amount-Leg 1
- Put amount-Leg 2
- Put currency-Leg 1
- Put currency-Leg 2
- Exchange rate
- Exchange rate basis
- First exercise date
- Fixed rate-Leg 1
- Fixed rate-Leg 2
- Option Premium Amount
- Option Premium Currency
- Price
- Price unit of measure
- Spread-Leg 1
- Spread-Leg 2
- Spread currency-Leg 1
- Spread currency-Leg 2
- Strike Price
- Strike price currency/currency pair
- Post-priced swap indicator
- Price currency
- Price notation
- Spread notation-Leg 1
- Spread notation-Leg 2
- Strike price notation
- Fixed rate day count convention-leg 1
- Fixed rate day count convention-leg 2
- Floating rate day count convention-leg 1
- Floating rate day count convention-leg 2
- Floating rate reset frequency period-leg 1
- Floating rate reset frequency period-leg 2
- Floating rate reset frequency period multiplier-leg 1
- Floating rate reset frequency period multiplier-leg 2
- Other payment amount
- Fixed rate payment frequency period-Leg 1
- Floating rate payment frequency period-Leg 1
- Fixed rate payment frequency period-Leg 2
- Floating rate payment frequency period-Leg 2
- Fixed rate payment frequency period multiplier-Leg 1
- Floating rate payment frequency period multiplier-Leg 1
- Fixed rate payment frequency period multiplier-Leg 2
- Floating rate payment frequency period multiplier-Leg 2
- Other payment type
- Other payment currency
- Settlement currency-Leg 1
- Settlement currency-Leg 2
- Settlement location-Leg 1
- Settlement location-Leg 2
- Collateralisation category
- Custom basket indicator
- Index factor
- Underlier ID-Leg 1
- Underlier ID-Leg 2
- Underlier ID source-Leg 1
- Underlying Asset Name
- Underlying asset subtype or underlying contract subtype-Leg 1
- Underlying asset subtype or underlying contract subtype-Leg 2
- Embedded Option type
- Option Type
- Option Style
- Package indicator
- Package transaction price
- Package transaction price currency
- Package transaction price notation
- Package transaction spread
- Package transaction spread currency
- Package transaction spread notation
- Physical delivery location-Leg 1
- Delivery Type
```

## SEC Form D Data

SEC Form D data is organized in quarterly archives containing TSV files. Each quarterly archive (e.g., `2020q1_d.zip`) contains a nested directory structure:

```
2020q1_d/
└── 2020Q1_d/
    ├── FORMDSUBMISSION.tsv
    ├── ISSUERS.tsv
    ├── OFFERING.tsv
    ├── RECIPIENTS.tsv
    ├── RELATEDPERSONS.tsv
    └── SIGNATURES.tsv
```

### Form D TSV File Structures:

**FORMDSUBMISSION.tsv** - Main submission data:
- ACCESSIONNUMBER (Primary Key)
- SUBMISSIONTYPE
- TESTFILINGFLAG
- LIVEFILINGFLAG
- DATEOFSUBMISSION
- DATEOFRECEIPTBYCOMMISSION
- PRIMARYISSUERCIK
- PRIMARYISSUERNAME
- PRIMARYISSUERSTATECOUNTRYOFINCORPORATION
- PRIMARYISSUERSTATECOUNTRYOFINCORPORATIONDESCRIPTION
- ENTITYTYPE
- ENTITYTYPEDESCRIPTION
- YEAROFINCORPORATION
- TOTALOFFERINGAMOUNT
- TOTALAMOUNTSOLD
- TOTALREMAINING
- CLARIFICATIONOFRESPONSE
- SIGNATURENAME
- SIGNATURETITLE
- SIGNATUREDATE

**ISSUERS.tsv** - Issuer information:
- FORMD_ISSUER_SK (Auto-increment Primary Key)
- ACCESSIONNUMBER (Foreign Key)
- ISSUERCIK
- ISSUERNAME
- ISSUERSTATECOUNTRYOFINCORPORATION
- ISSUERSTATECOUNTRYOFINCORPORATIONDESCRIPTION
- ENTITYTYPE
- ENTITYTYPEDESCRIPTION
- YEAROFINCORPORATION
- ISSUERADDRESSSTREET1
- ISSUERADDRESSSTREET2
- ISSUERADDRESSCITY
- ISSUERADDRESSSTATEORCOUNTRY
- ISSUERADDRESSSTATEORCOUNTRYDESCRIPTION
- ISSUERADDRESSZIPCODE
- ISSUERPHONENUMBER
- RELATIONSHIPCLARIFICATION

**OFFERING.tsv** - Offering details:
- FORMD_OFFERING_SK (Auto-increment Primary Key)
- ACCESSIONNUMBER (Foreign Key)
- INDUSTRYGROUP
- INDUSTRYGROUPTYPE
- INVESTMENTFUNDTYPE
- INVESTMENTFUNDTYPEDESCRIPTION
- ISFEEDERORFUND
- TYPEOFFILINGFLAG
- NEWFILINGFLAG
- AMENDMENTFLAG
- DATEOFFIRSTSALE
- DURATIONOFOFFERING
- TYPEOFSECURITYOFFERED
- BUSINESSCOMBINATIONTRANSACTIONFLAG
- MINIMUMINVESTMENTACCEPTED
- SALESCOMPENSATIONRECIPIENTFLAG
- OFFERINGSALESCOMPENSATIONFLAG
- FINDERSFEESFLAG
- SALESCOMPENSATIONDESCRIPTION

**RECIPIENTS.tsv** - Sales compensation recipients:
- FORMD_RECIPIENT_SK (Auto-increment Primary Key)
- ACCESSIONNUMBER (Foreign Key)
- RECIPIENTCIK
- RECIPIENTNAME
- ASSOCIATEDBROKERDEALER
- ASSOCIATEDBROKERDEALERCRD
- RECIPIENTADDRESSSTREET1
- RECIPIENTADDRESSSTREET2
- RECIPIENTADDRESSCITY
- RECIPIENTADDRESSSTATEORCOUNTRY
- RECIPIENTADDRESSSTATEORCOUNTRYDESCRIPTION
- RECIPIENTADDRESSZIPCODE
- RECIPIENTPHONENUMBER

**RELATEDPERSONS.tsv** - Related person information:
- FORMD_RELATED_PERSON_SK (Auto-increment Primary Key)
- ACCESSIONNUMBER (Foreign Key)
- RELATEDPERSONNAME
- RELATEDPERSONADDRESSSTREET1
- RELATEDPERSONADDRESSSTREET2
- RELATEDPERSONADDRESSCITY
- RELATEDPERSONADDRESSSTATEORCOUNTRY
- RELATEDPERSONADDRESSSTATEORCOUNTRYDESCRIPTION
- RELATEDPERSONADDRESSZIPCODE
- RELATEDPERSONPHONENUMBER
- RELATEDPERSONRELATIONSHIPCLARIFICATION

**SIGNATURES.tsv** - Signature information:
- FORMD_SIGNATURE_SK (Auto-increment Primary Key)
- ACCESSIONNUMBER (Foreign Key)
- SIGNATURENAME
- SIGNATURETITLE
- SIGNATUREDATE

## Other SEC Data

The following directories have not been implemented yet:

- `SecNcen` - SEC N-CEN forms (Investment Company Annual Report)
- `SecNport` - SEC N-PORT forms (Monthly Portfolio Holdings Report)
- `Sec13F` - SEC 13F forms (Institutional Investment Manager Holdings Report)
- `SecNmfp` - SEC N-MFP forms (Money Market Fund Monthly Report)
- `FOREX` - Foreign Exchange data
- `EDGAR` - SEC EDGAR filings
- `EXCHANGE` - Exchange data
- `INSIDERS` - Insider trading data

These can be implemented following the same pattern as Form D processing.
