<template>
  <Export
    :shots="shots"
    :assets="assets"
    :current-episode-no="currentEpisodeNo"
    :workflow-stage="workflowStage"
    @shots-updated="$emit('shots-updated', $event)"
  />
</template>

<script>
import Export from '../components/Export.vue';

export default {
  name: 'ExportView',
  components: { Export },
  props: {
    shots: {
      type: Array,
      default: () => []
    },
    assets: {
      type: Array,
      default: () => []
    },
    currentEpisodeNo: {
      type: Number,
      required: true
    },
    workflowStage: {
      type: String,
      default: 'export-stage'
    }
  },
  emits: ['shots-updated']
};
</script>
