import { createRouter, createWebHashHistory } from 'vue-router';
import AssetsCastingView from '../views/AssetsCastingView.vue';
import DirectorWorkbenchView from '../views/DirectorWorkbenchView.vue';
import ExportView from '../views/ExportView.vue';
import LLMConfigView from '../views/LLMConfigView.vue';
import ScriptStoryboardView from '../views/ScriptStoryboardView.vue';

const routes = [
  {
    path: '/',
    redirect: { name: 'script-storyboard' }
  },
  {
    path: '/script',
    name: 'script-storyboard',
    component: ScriptStoryboardView
  },
  {
    path: '/assets',
    name: 'assets-casting',
    component: AssetsCastingView
  },
  {
    path: '/workbench',
    name: 'director-workbench',
    component: DirectorWorkbenchView
  },
  {
    path: '/export',
    name: 'export-stage',
    component: ExportView
  },
  {
    path: '/llm-config',
    name: 'llm-config',
    component: LLMConfigView
  },
  {
    path: '/script-input',
    redirect: { name: 'script-storyboard' }
  },
  {
    path: '/storyboard',
    redirect: { name: 'script-storyboard' }
  },
  {
    path: '/scene-style',
    redirect: { name: 'assets-casting' }
  },
  {
    path: '/character-library',
    redirect: { name: 'assets-casting' }
  },
  {
    path: '/keyframes',
    redirect: { name: 'director-workbench' }
  },
  {
    path: '/veo-video',
    redirect: { name: 'director-workbench' }
  },
  {
    path: '/montage',
    redirect: { name: 'export-stage' }
  },
  {
    path: '/output',
    redirect: { name: 'export-stage' }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: { name: 'script-storyboard' }
  }
];

const router = createRouter({
  history: createWebHashHistory(),
  routes
});

export default router;
