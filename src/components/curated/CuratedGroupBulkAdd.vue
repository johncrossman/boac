<template>
  <div>
    <div class="mt-3 w-75">
      <div v-if="error || warning" class="alert-box p-3 mt-2 mb-3 w-100" :class="{'error': error, 'warning': warning}">
        <span aria-live="polite" role="alert" v-html="error || warning"></span>
      </div>
      <div>
        <b-form-textarea
          id="curated-group-bulk-add-sids"
          v-model="textarea"
          aria-label="Type or paste student SID numbers here"
          rows="8"
          max-rows="30"
          :disabled="isSaving"
        ></b-form-textarea>
      </div>
      <div class="d-flex justify-content-end mt-3">
        <b-btn
          id="btn-curated-group-bulk-add-sids"
          class="pl-2"
          variant="primary"
          :aria-label="curatedGroupId ? 'Add SIDs to current group' : 'Next, create curated group'"
          :disabled="!trim(textarea) || isSaving"
          @click="submitSids">
          {{ curatedGroupId ? 'Add' : 'Next' }}
        </b-btn>
        <b-btn
          v-if="curatedGroupId"
          id="btn-cancel-bulk-add-sids"
          variant="link"
          :aria-label="curatedGroupId ? 'Add SIDs to current group' : 'Next, create curated group'"
          @click="cancel">
          Cancel
        </b-btn>
      </div>
    </div>
  </div>
</template>

<script>
import Util from '@/mixins/Util';
import { validateSids } from '@/api/student';

export default {
  name: 'CuratedGroupBulkAdd',
  mixins: [Util],
  props: {
    bulkAddSids: Function,
    curatedGroupId: Number
  },
  data: () => ({
    error: undefined,
    isSaving: false,
    sids: undefined,
    textarea: undefined,
    warning: undefined
  }),
  created() {
    this.putFocusNextTick('curated-group-bulk-add-sids');
  },
  methods: {
    cancel() {
      this.clearErrors();
      this.bulkAddSids(null);
    },
    clearErrors() {
      this.error = null;
      this.warning = null;
    },
    describeNotFound(sidList) {
      if (sidList.length === 1) {
        return `<strong>Uh oh!</strong> Student ${sidList[0]} not found. Please fix.`;
      } else {
        return `<strong>Uh oh!</strong> ${sidList.length} students not found: <ul class="mt-1 mb-0"><li>${this.join(sidList, '</li><li>')}</li></ul>`;
      }
    },
    submitSids() {
      this.sids = [];
      this.clearErrors();
      const trimmed = this.trim(this.textarea, ' ,\n\t');
      if (trimmed) {
        const split = this.map(this.split(trimmed, ','), entry => {
          return this.trim(entry, ' ,\n\t');
        });
        const notNumeric = this.partition(split, sid => /^\d+$/.test(this.trim(sid)))[1];
        if (notNumeric.length) {
          this.error = '<strong>Error!</strong> The list provided has not been properly formatted. Please fix.';
        } else {
          this.isSaving = true;
          validateSids(split).then(data => {
            const notFound = [];
            this.each(data, entry => {
              switch(entry.status) {
                case 200:
                case 401:
                  this.sids.push(entry.sid);
                  break;
                default:
                  notFound.push(entry.sid);
              }
            });
            if (notFound.length) {
              this.warning = this.describeNotFound(notFound);
              this.isSaving = false;
            } else {
              this.clearErrors();
              this.bulkAddSids(this.sids);
            }
          });
        }
      } else {
        this.warning = 'Please provide one or more SIDs.';
      }
    }
  }
}
</script>

<style scoped>
.alert-box {
  border-radius: 5px;
  font-size: 18px;
  width: auto;
}
.error {
  background-color: #efd6d6;
  color: #9b393a;
}
.warning {
  background-color: #fbf7dc;
  color: #795f31;
}
</style>