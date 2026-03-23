<template>
  <ScriptStoryboard
    :current-episode-no="currentEpisodeNo"
    :initial-script="initialScript"
    :initial-duration="initialDuration"
    :initial-result="initialResult"
    :history="history"
    :workflow-stage="workflowStage"
    @script-generated="$emit('script-generated', $event)"
    @script-updated="$emit('script-updated', $event)"
    @history-selected="$emit('history-selected', $event)"
    @load-scenes-as-shots="$emit('load-scenes-as-shots', $event)"
  />
</template>

<script>
import ScriptStoryboard from '../components/ScriptStoryboard.vue';

export default {
  name: 'ScriptStoryboardView',
  components: { ScriptStoryboard },
  props: {
    currentEpisodeNo: {
      type: Number,
      required: true
    },
    initialScript: {
      type: String,
      default: ''
    },
    initialDuration: {
      type: String,
      default: '3min'
    },
    initialResult: {
      default: null
    },
    history: {
      type: Array,
      default: () => []
    },
    workflowStage: {
      type: String,
      default: 'script-storyboard'
    }
  },
  emits: ['script-generated', 'script-updated', 'history-selected', 'load-scenes-as-shots']
};
</script>
