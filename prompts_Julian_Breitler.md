# GIS Land Eligibility Analysis - Project Prompts Documentation
Author of Prompts: **Julian Breitler**

These prompts were used  in multiple LLM (mostly Claude Sonnet 4.5 and Grok Code). 

Some of them were used in IDE'S like Cursor or terminal tools like Claude Code.

Some prompts were left out due to repetition (integrating input handling via config file).

Prompts about Git and Github problems/questions are not included. For that mostly ChatGPT and Gemini was used. 

## 1. Project Setup

**Model:** Claude Sonnet 4.5

### Initial Planning Prompt
```
Can you take a look at this scientific paper and help me creating a detailed plan 
for recreating the methodology. Focus on the Land eligibility method for now and 
report back when you think you are done with that part and made a plan that can 
be followed. I am planning on recreating this GIS analysis for a part of Austria 
in a much smaller scale and use Python to do this so keep this in mind.

List potential packages to use and compare their strengths and weaknesses for 
the task.
```
This worked well and I got a good overview of the project and a plan that made the scope of the project understandable, but it lacked in detail, which was ok for that stage of our project.

### Export Plan Documentation
```
Can you give me a markdown file for the first section of your plan (up until 
the Python package comparison)?
```
Worked well.

## 2. Creating Project Structure

**Model:** Grok Code in Cursor

### File Structure Setup
```
Create a proper file structure. We want to fill the README.md file with our 
overall goal and plan for executing our project. If you are not 90% sure, ask 
me for clarification. Only do one step at a time.
```
This prompt worked quite well, but the AI got overmontivated and created files unrelevant files  that I had to delete later on. 

## 3. Creating Slope Calculation

**Model:** Grok Code

### Initial Slope Script
```
I have a SRTM DEM and I want to calculate the slope for this dataset. Can you 
help me with a Python script? Use simple logic and think like a beginner. Check 
in if you are not 90% sure what to do.
```
worked well, the script was wuite usable but got replaced later on with the current slope_exculsion script.

## 4. Boolean Raster Region Mask

**Model:** Claude Sonnet 4.5

### Understanding the Task
```
Can you now focus on this task specifically: "Create initial region mask (Boolean 
raster covering entire area)". How can I do this? What is the input needed? How 
are the authors doing this? Maybe describe it in QGIS Desktop GUI steps on what 
to do so I can really understand the steps needed.
```
This was quite useful to get a step by step instruction on how to do this in qgis first
to understand the result and the workflow. That lead to better prompting in the futrue and 
and overall better understanding of the method.

### CRS Validation
```
Ok let's look at the example code. I want to make sure the correct CRS gets used. 
Could you give me an example of how you could add a clause to make sure the input 
.shp is in the correct CRS and if not either throw an error or reproject it to 
the correct one (i.e. WGS 84 / UTM zone 33N: EPSG 32633). Just give me code 
snippets and explain exactly what you are doing.
```
Also quite usefull eventhough in the end it would have been better to just use this CRS check in the inital shapefile/raster handling scripts (clip/reproject). Now it violates the "d.r.y" principle. 

### Path Configuration for GitHub Collaboration
```
I am working in a git folder which I am sharing with colleagues over GitHub. The 
script should work for them as well. My raster_region_mask.py file is in this 
folder "C:...\GIS_2_midterm\scripts\preprocessing". I am running a venv in my 
git folder "GIS_2_midterm". For now I hardcoded the input path for my .shp 
boundary file. I want to change this. Explain what to do and walk me through the 
process of setting up efficient and flexible input/output paths.
```
Worked well to implement a "config-file" workflow. The LLM provided different solution with different levels of compelxity as well as their benefits and weaknesses.

## 5. Vector to Raster Conversion (and Batch Process Exclusion)

**Model:** Claude Sonnet 4.5

### Initial Script Creation
```
I want to create a script that converts vector data to raster data, so I can use 
it as input for the land eligibility analysis. Explain each step and what 
everything does. I guess it will look quite similar to the raster region mask, 
am I right (but with different values burnt in)?
```
This prompt created multiple scripts, some of them quite complex and with some code parts which i discared earlier. It also added parts to the process which I hadn't mentioned i wanted. The prompt should have been more precise. In the next prompt I tried to improve the
the answers with more context.

### Simplification for Testing
```
What if I already created buffers for the vector data in a different preprocessing 
step? What are the things to look out for? Which option is better/worse? Also 
please simplify the script for now. For testing I want to use hardcoded input 
paths and no config file. Just hardcoded input parameters and so on. I want to 
test it before and then add those advanced features. So for now we just want to 
keep the "load vector data" and the "CRS validation". No attribute filter and 
no buffer.
```
This then lead to a better result.

### Understanding Masking Logic
```
So the vector_to_raster_simple.py not only converts the vector data to raster 
but also already masks it not the raster_region_mask and creates a raster which 
has already the excluded areas, am I correct? So if that is so I would need to 
do this to all vector files which I want to consider in my analysis. Tell me if 
my thoughts are correct. Also how are other raster data handled (like slope)?
```
Resulted in a good explaination of the method/concept which cleared up some questions.

### Batch Processing Implementation
```
What is the simplest or most robust way to "loop" through all the vector files 
to calc raster exclusion for each vector layer? Maybe present me with a simple 
beginner friendly version and some advanced option.
```
Worked well, but needed some manual editing and a few small follow-up prompts which ultimatly lead to the config file implementaion. 

## 6. Slope Calculation Refinement

**Model:** Claude Sonnet 4.5

### Elevation vs Slope Exclusion
```
You provided me with a script for slope exclusion. What if I want to do the same 
for elevation? Can this also be handled in 1 script just like for vector or would 
it be cleaner to do both separate? Also does it make more sense to first calculate 
the slope from a DEM in a script and then do the exclusion or is it better to do 
it both in 1 script like you did? Discuss this.
```
This was used for general understanding how such things are handled efficiently and how I could do this in future projects.

### Resampling Fix
```
Can you help me with adding a resampling code to my script? My raster dimensions 
don't match.
```
The LLM added a commet about resampling but didn't add it to the code therefore a crash occured and I had to help it along with some more prompts. Maybe the prompts cloud have been more accurate but I did't understand the whole concept/scope of the project at this point. 
---

## 7. Config File Implementation

**Model:** Claude Sonnet 4.5 in Claude Code

### Creating Config System
```
Can you take a look at my project and update/create a config file which handles 
data input for the different scripts? The @config.py already exists but needs to 
be redone. Look at the data folder. Tell me everything you do and ask me if you 
are not 95% sure. Also give me a walk through on how this config file is used, 
I never used something like this. Don't change any of the other scripts for now.
```
This worked well for implementing the config-file workflow.

### Adding Documentation
```
Ok that sounds great, could you add comments to the config file which explain 
what is happening? They don't have to be very detailed but should be understandable 
by beginners.
```
This helped to make it more readable. Should have added this to the first prompt.

### First Script Integration
```
Ok now since that is set up, let's implement this. We will start with 1 script 
first so I can see how this works. Let's adjust @reproject_clip_dem.py
```
Worked well

### PROJ Library Error Handling
```
(In the context of an occurring PROJ Library error - See config.py line 25-36)

Yes please add this to the config.py. Does this only occur on my machine? Will 
my colleagues also need this?
```
And Error occroud (Windows Enviromental Variable Error due to conflicts with POST-GIS and PostGres installation) which would have taken long to correct without the AI. But cloud be that this only occured because of the config-file structure / input-output-handling approach. 

### Second Script Integration
```
Let's do the same for reproject_clip_shps.py
```
Worked well

## 8. Master Exclusion Script

**Model:** Claude Sonnet 4.5 in Claude Code

### Creating Master Exclusion
```
Now let's create the master_exclusion script. We want to loop over all exclusion 
files to get the final exclusion raster. As the baseline raster use the 
raster_region_mask.tif. Explain everything you do and what the outcome is. Do 
you know what to do or what the outcome should be? If you are not 90% sure ask me.
```
This worked well ad created a working script with good documentation.

## 9. LCOE Calculation

**Model:** Claude Sonnet 4.5 in Claude Code

### Config File Integration
```
Ok now I want to change the input of the Output_LCOE_Potential.py so it works 
with the config file. Do this in the same style as all the other scripts. Check 
in with me for the changes and don't alter anything that isn't necessary to 
complete the task that I gave you. Look at the folder preprocessing and the files 
raster_region_mask.py or batch_process_vector_to_raster_exclusion.py for input 
handling. Proceed with the changes to Output_LCOE_Potential.py
```
 The config-file input/output handling was implemented correctly but this lead to using the wrong input data and therefore proucing nonsense. The prompt should have been more specific about what to use. 

### Correcting Input File
```
Ok that worked great. Now I want to change the input of Output_LCOE_Potential.py. 
We used the wrong file for the Region mask. We want to use the output of the 
master_exclusion.py as the input. Does this output already exist in the config 
file? Tell me what I need to adjust to do that.
```
resolved the issue with the wrong input. 

## 10. README Documentation

**Model:** Claude Sonnet 4.5 in Claude Code

### Update File Structure Documentation (used multiple times)
```
Please update the README.md file with the changes we have made to the file 
structure and the workflow.
```
Worked in the begining but but lacked detail in the end. At a sertain level the AI did't change anything anymore or overlooked things.

### Document Script Execution Order
```
Also make it clear in the README what the correct order is to run the scripts in.
```
Worked well

## 11. Prompts File

**Model:**  Claude Sonnet 4.5

### Create Prompt Makrdown
```
take a look at this .txt file. it contains the prompts i used for my project. format the .txt file and give me a .md file, don't change any text. 
```
Worked well for basic .md file
