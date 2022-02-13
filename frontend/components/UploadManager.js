import FileUpload from './FileUpload.js'
import { useForm, UseFormRegisterReturn } from 'react-hook-form'
import { Button, FormControl, FormErrorMessage, FormLabel, Icon, InputGroup } from '@chakra-ui/react'
import { FiFile } from 'react-icons/fi'



export default function UploadManager() {
  const {register, handleSubmit, formState: {errors}} = useForm()
  const onSubmit = handleSubmit((data) => console.log('On Submit: ', data))

  const validateFiles = (value) => {
    if (value.length < 1) {
      return 'Upload at least one image'
    }
    return true
  }

  return (
    <>
      <form onSubmit={onSubmit}>
        <FormControl isInvalid={!!errors.file_} isRequired>
          <FormLabel>{'File input'}</FormLabel>
          <FileUpload
            accept={'image/*'}
            register={register('file_', {validate: validateFiles})}
          >
            <Button leftIcon={<Icon as={FiFile} />}>
              Upload
            </Button>
          </FileUpload>

          <FormErrorMessage>
            {errors.file_ && errors?.file_.message}
          </FormErrorMessage>
        </FormControl>
      </form>
    </>
  )
}