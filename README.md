<H1>Read Me - LLM-NHS-Winter-Pressure-synthesis</H1>

- This script is designed as part of a wider research project with Oxford University's Nuffield Department of Primary Care Health Science. 

- As there are multple API calls to many models, the decision to use LiteLLM, the Open-source AI gateway <litellm==1.91.3>. 

- Simalary, for the API calls themselves, the script utlises an Open_router API key. This is essential to the automation, and so you must have an Open_router API key. 

The models can be changed as long as they are supported by both LiteLLM and Open_router:

The models used are:
* -DeepSeek V4
* -Open AI luna 
* -Claude Sonnet 
* -Googel Gemini
* -Tencent Hy3

<H2> How the script works: </H2>

Dependencies and changes to file format:
 - For alterations/ additions to the <New_Personas.txt>, follow the clear pattern whereby the new persona data follows precisely  the string '####'.
  - Additionally, other promopts should be changed at the disgression of the new user.
  - All task prompt files are clearly names to match the method they are used in.
 
Script Notes:
 - This script is designed to be as reproducable, and open sourced as possible, this means all steps, meaning all 5 models x 7 persona outputs are written to a files.
  - Additionally, all intermediate outputs before the final cross model analysis are also printed to their respective files.
  - All outputs are printed to the <LLM_project_outputs> folder, this folder is created if its not found in the working directory.   




For further contact and questions find me, ilprutter@gmail.com
