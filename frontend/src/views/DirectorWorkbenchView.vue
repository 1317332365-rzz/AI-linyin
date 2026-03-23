<template>
  <DirectorWorkbench
    :assets="assets"
    :shots="shots"
    :storyboard-scenes="storyboardScenes"
    :video-provider="videoProvider"
    :current-episode-no="currentEpisodeNo"
    :workflow-stage="workflowStage"
    @shots-updated="$emit('shots-updated', $event)"
    @generated-event="$emit('generated-event', $event)"
  />
</template>

<script>
import DirectorWorkbench from '../components/DirectorWorkbench.vue';

export default {
  name: 'DirectorWorkbenchView',
  components: { DirectorWorkbench },
  props: {
    assets: {
      type: Array,
      default: () => []
    },
    shots: {
      type: Array,
      default: () => []
    },
    storyboardScenes: {
      type: Array,
      default: () => []
    },
    videoProvider: {
      type: String,
      default: 'openai'
    },
    currentEpisodeNo: {
      type: Number,
      required: true
    },
    workflowStage: {
      type: String,
      default: 'director-workbench'
    }
  },
  emits: ['shots-updated', 'generated-event']
};
</script>
