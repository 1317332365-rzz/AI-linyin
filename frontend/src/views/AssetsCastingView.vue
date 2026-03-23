<template>
  <AssetsCasting
    :assets="assets"
    :storyboard-scenes="storyboardScenes"
    :story-package="storyPackage"
    :script-input="scriptInput"
    :script-duration="scriptDuration"
    :workflow-stage="workflowStage"
    @asset-added="$emit('asset-added', $event)"
    @asset-deleted="$emit('asset-deleted', $event)"
    @script-updated="$emit('script-updated', $event)"
  />
</template>

<script>
import AssetsCasting from '../components/AssetsCasting.vue';

export default {
  name: 'AssetsCastingView',
  components: { AssetsCasting },
  props: {
    assets: {
      type: Array,
      default: () => []
    },
    storyboardScenes: {
      type: Array,
      default: () => []
    },
    storyPackage: {
      default: null
    },
    scriptInput: {
      type: String,
      default: ''
    },
    scriptDuration: {
      type: String,
      default: '3min'
    },
    workflowStage: {
      type: String,
      default: 'assets-casting'
    }
  },
  emits: ['asset-added', 'asset-deleted', 'script-updated']
};
</script>
