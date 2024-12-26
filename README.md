# Hermione

This is a ***POC (Proof Of Concept)*** project to show that it is possible
to manage compatibility between licenses in a new way.

# Existing approaches

There are two approaches of providing license compatibility data:

* graph

* matrix

## Missing context

Compatiblity between two licenses, at least when it comes to the Hermione project, is defined as

* can I use a component under license B
* in my program which I want to release under license A

The answer to this depends on the context, such as:

* Usecase

* Provisioning

* Modification

For more information about the context, see [Licomp](https://github.com/hesa/licomp)

## Hermione goals

The goal with Hermione was (perhaps even is) to switch from looking at
license compatibility to looking at compatibility between license
clauses. We base our POC on
[hermine-data](https://gitlab.com/hermine-project/hermine-data) (part
of [Hermine](https://hermine-foss.org/))

## Examples of the existing approaches

### Graph

* David Wheeler's [The Free-Libre / Open Source Software (FLOSS) License Slide](https://dwheeler.com/essays/floss-license-slide.html)

* GNU's [A Quick Guide to GPLv3](https://www.gnu.org/licenses/quick-guide-gplv3.html)

### Matrix

* PKU-SEI's [RecLicense](https://github.com/osslab-pku/RecLicense)

* OSADL's [license matrix](https://www.osadl.org/fileadmin/checklists/matrix.json)

### Accessing existing resources via Licomp

While creating Hermione we wrote a generic API,
[Licomp](https://github.com/hesa/licomp), to access License
Compatibility resources, such as the above, using one API. We also
wrote a tool to access some of the resources using this API:
[licomp-toolkit](https://github.com/hesa/licomp-toolkit)

Currently the following Licomp implementations exist:

* [licomp-hermione](https://github.com/hesa/licomp-hermione) - yes, this project

* [licomp-osadl](https://github.com/hesa/licomp-osadl)

* [licomp-proprietary](https://github.com/hesa/licomp-proprietary)

* [licomp-reclicense](https://github.com/hesa/licomp-reclicense)

* [licomp-dwheeler](https://github.com/hesa/licomp-dwheeler)

## Hermione approach

### Background

Hermine-data has roughly 30 clauses. We started out by creating a
clause matrix, of size 30 * 30 = 900. When using colors (yes=green,
no=red, else=yellow) we noticed that most of the values are yes (as in
the licenses are compatible). We decided to take yes as the deafult
and somehow write down the no and so on.

The clauses can be found in [clause_matrix.p](https://github.com/hesa/hermione/blob/main/scripts/clause_matrix.py)

#### No further restrictions

Looking at [GNU General Public License, version 2](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html) and more specifically at clause 6, we can read " You may not impose any further restrictions on the recipients' exercise of the rights granted herein.". If GPLv2 is the outbound license, then

* BSD-3-Clause as inbound is OK

* Apache-2.0 is inbound is not OK - since the patent clause in Apache-2.0 would be a "further restriction".

Our solution is to:

* allow for tagging a clause as restrictive - this is a bit unfortunate since the tag is related to GPLv2

* check if the inbound license's clauses are not both

    * a restriction (see above)

    * not present in the license

To be able to determine if the inbound can be used with the outbound we need context for the decision. The context is:

* outbound license and its clauses

* inbound license and its clauses

#### Copyleft

Again, looking at GPLv2 and the copyleft effect. If GPLv2 is the inbound license, then 

* BSD-3-Clause as outbound is not OK - since GPLv2 requires using the same license

* GPLv2 as outbound is not OK - since the inbound and outbound are the same license

So, again, we need the same context as above to detemine if the inbound license can be used with the outbound license.

### Hermine language

Yeah, it is kind of pompous to call it a language. Anyhow, here are the ideas.

#### Compatible

The term "Preserve legal mentions in source code" as part of an inbound license is compatible with every license so we can state the compatibility with outbound clasues as:

```
    "Preserve legal mentions in source code": {},
```

When executed Hermione will check if the clause has any possible incompatibilities, but since the dictionary is empty the compatibility is yes.

*Note: that the name here comes from hermine-date.*

#### Calculated

When writing an expression for the compatiblitiy between two clauses you can use the following keywords:

#### Context

* `and` - logical and operator

* `has obligtion <OBLIGATION NAME>` - e.g. `"inbound_license has obligation \"Strong Copyleft\" `

* `has not obligtion <OBLIGATION NAME>` - e.g. `"inbound_license has not obligation \"Strong Copyleft\" `

* `inbound_license` - the inbound license

* `inbound_obligation` - the examnined obligation of the inbound license

* `is excepted` - e.g. `inbound_obligation is excepted`

* `or`  - logical or operator

* `outbound_license` - the outbound license

* `outbound_obligation` - the examnined obligation of the outbound license

#### inbound_expression

"inbound_expression": "inbound_license same as outbound_license or inbound_obligation is excepted"

#### outbound_expression

        "outbound_expression": "inbound_license has not obligation \"Strong Copyleft\" or inbound_license same as outbound_license"
        "restriction": True

### Restricted

## Result

A license compatibility matrix per each combination of:

* provisining case

* modification

is created by looping thrugh the licenses and checking the clauses. It does take quite a while to produce these license compatibility matrices but once done they can be used quickly by tools such as [flict](https://github.com/vinland-technology/flict) and [licomp-hermione](https://github.com/hesa/licomp-hermione).


To create the license compatibility mnatrices:

```
./scripts/hermine_data.py
```
