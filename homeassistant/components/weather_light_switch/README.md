# Weather Light Switch
As part of the course Software Evolution Project in Chalmers/Gothenburg University, we have extended the Hue Light integration in Home Assistant. Philips Hue Lights are known for their vast options to change their lights depending on different scenarios to create different moods. However, in Home Assistant these features are limited. We provide an additional way of automating your lights depending on your environment. This is to give a user more options to customize their Hue Lights to their satisfaction. We have also created another feature found in `/components/music_light_switch`

### Feature
Make the Hue Lights change depending on what weather condition it is.

## Requirements
Firstly, you need to have a Hue setup at home. From there on you can connect it to [Home Assistant](https://www.home-assistant.io/integrations/hue/). Afterwards, create the switch that turn the feature on. This is done in the Home Assistant dashboard. Settings --> Devices & services --> Helpers. Here you create a helper using the _Weather Light Switch_. Connect the Weather Switch to a weather integration and the light. Now the switch can be added in the dashboard. Turn on the switch to activate the feature

