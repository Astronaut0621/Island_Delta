# Island Delta

Island Delta is an anonymous emotion-map product where users leave location-bound emotional records that can be aggregated into emotion layers and optional temperature views.

## Language

**Emotion Record**:
An anonymous, location-bound user expression containing a text story, a primary emotion, a sentiment, a temperature, and a safety level.
_Avoid_: Post, message, note

**Sentiment**:
The coarse emotional polarity of an expression: positive, neutral, or negative. In the first MVP model, it is derived from the primary emotion instead of being predicted as an independent model output.
_Avoid_: Emotion, mood

**Primary Emotion**:
The single most important fine-grained emotion label for an expression: lonely, anxious, stressed, tired, sad, calm, healed, secure, happy, or hopeful. A text can imply multiple feelings, but the MVP dataset labels only one dominant primary emotion.
_Avoid_: Sentiment, emotion score, multi-label emotion

**Emotion Temperature**:
A numeric value from -10 to +10 that represents emotional intensity and warmth. It is an optional enhancement for the MVP emotion map, not the primary interaction or first model-training target.
_Avoid_: Score, rating

**Emotion Map**:
A map layer that visualizes the distribution of primary emotions across locations. In the MVP, this takes priority over temperature heatmaps.
_Avoid_: Temperature map, generic heatmap

**Safety Level**:
The content-risk category for an expression: normal, warning, or crisis. It governs whether an expression is suitable for public map display.
_Avoid_: Sentiment, moderation status

**Island Echo**:
The emotional companion agent that helps users organize feelings into a primary emotion, sentiment, temperature, and draft public expression.
_Avoid_: Chatbot, therapist, customer service
