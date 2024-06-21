# Multimodal AI for Movie Metadata Context Enrichment
## Overview
This is a multimodal AI project that enriches movie metadata by combining movie trailers (video) and text descriptions (plot). By integrating these two data types, we create enriched metadata, specifically a comprehensive synopsis, which can enhance search and recommendation services on streaming platforms.

## How does it work?
### Movie Trailers
For the video modality, a sequence of image frames (video can only be processed as images by the large language model) from the trailer is passed to OpenAI's GPT-4 model for image translation. A description is created from each frame with prompting for context. A chunking strategy is implemented to adhere to token limitations. The descriptions are then combined to create an overall visual summary.

### Plot
The plot for each trailer is sourced from a 3rd party service (OMDB API), which serves as the text modality for the project.

### Synopsis
The synopsis is created by combining the visual summary and plot using OpenAI. This final synopsis may be used for training models or creating embeddings.

## Conclusion
Integrating multiple input modalities, such as visual and textual data, significantly enhances the contextual richness of metadata. This multimodal approach enables a more comprehensive understanding and interaction, closely mirroring how humans perceive and process information. By leveraging both video and text, multimodal AI offers a nuanced and enriched representation of content that goes beyond the capabilities of single-modality data.