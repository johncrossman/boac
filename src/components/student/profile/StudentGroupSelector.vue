<template>
  <div>
    <b-dropdown id="curated-group-dropdown-select"
                class="curated-selector"
                :variant="dropdownVariant"
                toggle-class="b-dd-primary-override"
                size="sm"
                no-caret
                :disabled="disableSelector || groupsLoading">
      <template slot="button-content">
        <span :id="isAdding ? 'added-to-curated-group' : (isRemoving ? 'removed-from-curated-group' : 'add-to-curated-group')"
              class="p-3">
          <span v-if="!isAdding && !isRemoving">
            <span class="pr-2">Add to Group</span>
            <i class="fas fa-spinner fa-spin" v-if="disableSelector || groupsLoading"></i>
            <i class="fas fa-caret-down" v-if="!disableSelector"></i>
          </span>
          <span v-if="isRemoving">
            <i class="fas fa-check"></i> Removed from Group
            <span role="alert"
                  aria-live="passive"
                  class="sr-only">Student removed from the selected group</span>
          </span>
          <span v-if="isAdding">
            <i class="fas fa-check"></i> Added to Group
            <span role="alert"
                  aria-live="passive"
                  class="sr-only">Student added to the selected group</span>
          </span>
        </span>
      </template>
      <b-dropdown-item v-if="!size(myCuratedGroups)">
        <span class="cohort-selector-zero-cohorts faint-text">You have no curated groups.</span>
      </b-dropdown-item>
      <div v-if="!groupsLoading">
        <b-dropdown-item :id="`curated-group-${group.id}-menu-item`"
                         class="b-dd-item-override"
                         v-for="group in myCuratedGroups"
                         :key="group.id">
          <input :id="`curated-group-${group.id}-checkbox`"
                 type="checkbox"
                 v-model="checkedGroups"
                 :value="group.id"
                 @click="groupCheckboxClick(group)"/>
          <label :id="`curated-group-${group.id}-name`"
                 :for="`curated-group-${group.id}-checkbox`"
                 class="cohort-checkbox-name pb-0 pt-0"
                 :aria-label="`${checkedGroups.includes(group.id) ? 'Add student to' : 'Remove student from'} group '${group.name}'`">{{ group.name }}</label>
        </b-dropdown-item>
      </div>
      <b-dropdown-divider></b-dropdown-divider>
      <b-dropdown-item>
        <b-btn id="create-curated-group"
               class="create-new-button mb-0 pl-0 text-dark"
               variant="link"
               v-b-modal="'modal'"
               aria-label="Create a new curated group">
          <i class="fas fa-plus"></i> Create New Curated Group
        </b-btn>
      </b-dropdown-item>
    </b-dropdown>
    <b-modal id="modal"
             @shown="focusModalById('create-input')"
             body-class="pl-0 pr-0"
             v-model="showModal"
             hide-footer
             hide-header-close
             title="Name Your Curated Group">
      <CreateCuratedGroupModal :sids="[ sid ]"
                               :create="modalCreateGroup"
                               :cancel="modalCancel"/>
    </b-modal>
  </div>
</template>

<script>
import CreateCuratedGroupModal from '@/components/curated/CreateCuratedGroupModal.vue';
import UserMetadata from '@/mixins/UserMetadata';
import Util from '@/mixins/Util';
import {
  addStudents,
  createCuratedGroup,
  getMyCuratedGroupIdsPerStudentId,
  removeFromCuratedGroup
} from '@/api/curated';

export default {
  name: 'StudentGroupSelector',
  mixins: [UserMetadata, Util],
  components: {
    CreateCuratedGroupModal
  },
  props: {
    sid: {
      type: String,
      required: true
    }
  },
  data: () => ({
    checkedGroups: undefined,
    groupsLoading: true,
    isAdding: false,
    isRemoving: false,
    showModal: false
  }),
  created() {
    getMyCuratedGroupIdsPerStudentId(this.sid).then(data => {
      this.checkedGroups = data;
      this.groupsLoading = false;
    });
  },
  computed: {
    disableSelector() {
      return this.isAdding || this.isNil(this.myCuratedGroups);
    },
    dropdownVariant() {
      return this.isAdding
        ? 'success'
        : this.isRemoving
          ? 'warning'
          : 'primary';
    }
  },
  methods: {
    groupCheckboxClick(group) {
      if (this.includes(this.checkedGroups, group.id)) {
        this.isRemoving = true;
        const done = () => {
          this.checkedGroups = this.remove(this.checkedGroups, group.id);
          this.isRemoving = false;
        };
        removeFromCuratedGroup(group.id, this.sid).finally(() =>
          setTimeout(done, 1000)
        );
      } else {
        this.isAdding = true;
        const done = () => {
          this.checkedGroups.push(group.id);
          this.isAdding = false;
        };
        addStudents(group, [this.sid]).finally(() => setTimeout(done, 1000));
      }
    },
    modalCreateGroup(name) {
      this.isAdding = true;
      this.showModal = false;
      let done = () => {
        this.isAdding = false;
      };
      createCuratedGroup(name, this.sids).then(setTimeout(() => done(), 2000));
    },
    modalCancel() {
      this.showModal = false;
    }
  }
};
</script>

<style scoped>
.create-new-button {
  font-size: 16px;
}
.curated-selector {
  height: 35px;
}
</style>