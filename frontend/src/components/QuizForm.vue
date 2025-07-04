<template>
  <div class="bg-light py-3 border-bottom">
    <div class="container d-flex align-items-center justify-content-between flex-wrap gap-2">
      <!-- Lesson -->
      <div class="form-group d-flex align-items-center gap-2">
        <label class="mb-0 fw-bold">Lesson:</label>
        <select class="form-select" v-model="selectedLessonId" @change="onLessonChange">
          <option disabled value="">Select</option>
          <option v-for="lesson in lessons" :key="lesson.lesson_id" :value="lesson.lesson_id">
            {{ lesson.lesson_name }}
          </option>
        </select>
      </div>

      <!-- Module -->
      <div class="form-group d-flex align-items-center gap-2">
        <label class="mb-0 fw-bold">Module:</label>
        <select class="form-select" v-model="selectedModuleId" @change="onModuleChange" :disabled="!filteredModules.length">
          <option disabled value="">Select</option>
          <option v-for="mod in filteredModules" :key="mod.module_id" :value="mod.module_id">
            {{ mod.module_title }}
          </option>
        </select>
      </div>

      <!-- Topic -->
      <div class="form-group d-flex align-items-center gap-2">
        <label class="mb-0 fw-bold">Topic:</label>
        <select class="form-select" v-model="selectedTopicId" :disabled="!filteredTopics.length">
          <option disabled value="">Select</option>
          <option v-for="topic in filteredTopics" :key="topic.topic_id" :value="topic.topic_id">
            {{ topic.topic_title }}
          </option>
        </select>
      </div>

      <!-- Submit -->
      <button class="btn btn-primary" @click="showQuiz" :disabled="!selectedTopicId">Show Quiz</button>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

const router = useRouter();
export default {
  name: 'QuizStarter',
  setup() {
    const lessons = ref([]);
    const modules = ref([]);
    const topics = ref([]);

    const selectedLessonId = ref('');
    const selectedModuleId = ref('');
    const selectedTopicId = ref('');

    const filteredModules = computed(() => {
      return modules.value.filter(module => module.lesson_id === selectedLessonId.value);
    });

    const filteredTopics = computed(() => {
      return topics.value.filter(topic => topic.module_id === selectedModuleId.value);
    });


//     const fetchInitialData = async () => {
//   // Replace API calls with static dummy data
//   lessons.value = [
//     { lesson_id: 1, lesson_name: 'Mathematics' },
//     { lesson_id: 2, lesson_name: 'Science' }
//   ];

//   modules.value = [
//     { module_id: 1, lesson_id: 1, module_name: 'Algebra' },
//     { module_id: 2, lesson_id: 1, module_name: 'Geometry' },
//     { module_id: 3, lesson_id: 2, module_name: 'Physics' },
//     { module_id: 4, lesson_id: 2, module_name: 'Chemistry' }
//   ];

//   topics.value = [
//     { topic_id: 1, module_id: 1, topic_name: 'Quadratic Equations' },
//     { topic_id: 2, module_id: 1, topic_name: 'Linear Equations' },
//     { topic_id: 3, module_id: 2, topic_name: 'Triangles' },
//     { topic_id: 4, module_id: 3, topic_name: 'Laws of Motion' },
//     { topic_id: 5, module_id: 4, topic_name: 'Acids and Bases' }
//   ];
// };

    const fetchInitialData = async () => {
      try {
        const [lessonsRes, modulesRes, topicsRes] = await Promise.all([
          fetch('/get_all_lessons'),
          fetch('/get_all_modules'),
          fetch('/get_all_topics'),
        ]);

        lessons.value = await lessonsRes.json();
        modules.value = await modulesRes.json();
        topics.value = await topicsRes.json();
      } catch (err) {
        console.error('Error fetching quiz data:', err);
      }
    };

    const onLessonChange = () => {
      selectedModuleId.value = '';
      selectedTopicId.value = '';
    };

    const onModuleChange = () => {
      selectedTopicId.value = '';
    };

    const showQuiz = async () => {
      try {
            const response = await axios.get(`${lesson_id}/module/${module_id}/topic/${topic_id}/quizzes`);
            router.push({
            name: 'QuizView',
            state: { quiz: response.data }
            });

      } catch (err) {
        console.error('Failed to load quiz:', err);
      }
    };

    onMounted(() => {
      fetchInitialData();
    });

    return {
      lessons,
      modules,
      topics,
      selectedLessonId,
      selectedModuleId,
      selectedTopicId,
      filteredModules,
      filteredTopics,
      onLessonChange,
      onModuleChange,
      showQuiz
    };
  }
};
</script>

<style scoped>
.form-group select {
  min-width: 160px;
}
</style>
